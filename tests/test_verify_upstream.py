"""Tests for the fail-closed TSAR upstream verifier."""
import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "tsar-cli" / "verify_upstream.py"
SPEC = importlib.util.spec_from_file_location("tsar_verify_upstream", MODULE_PATH)
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


def valid_manifest():
    return {
        "version": "1.2.3",
        "repository": "https://github.com/mohamedelghazali/TSAR",
        "lifecycle": {
            "check_url": "https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/manifest.yaml",
            "fetch_before_task": True,
            "fail_closed": True,
        },
        "enforcement": {"default_mode": "strict", "allow_advisory_fallback": False},
        "active_files": {
            "core": sorted(verifier.REQUIRED_CORE),
            "ai_security": ["rules/owasp-llm/llm01-prompt-injection.md"],
        },
    }


def test_accepts_valid_strict_manifest():
    version, groups = verifier.validate_manifest(valid_manifest())
    assert version == "1.2.3"
    assert set(groups["core"]) == verifier.REQUIRED_CORE


@pytest.mark.parametrize(
    "mutate",
    [
        lambda m: m.update(repository="https://example.com/TSAR"),
        lambda m: m["lifecycle"].update(fail_closed=False),
        lambda m: m["enforcement"].update(allow_advisory_fallback=True),
        lambda m: m["enforcement"].update(default_mode="advisory"),
        lambda m: m["active_files"]["core"].remove("system/LIFECYCLE.md"),
        lambda m: m["active_files"].update(ai_security=["rules/../secrets.md"]),
        lambda m: m["active_files"].update(ai_security=["system/LIFECYCLE.md"]),
        lambda m: m.update(version="latest"),
    ],
)
def test_rejects_invalid_manifest(mutate):
    manifest = valid_manifest()
    mutate(manifest)
    with pytest.raises(verifier.VerificationError):
        verifier.validate_manifest(manifest)


def test_main_pins_manifest_and_policy_reads_to_one_commit(monkeypatch, tmp_path):
    sha = "a" * 40
    manifest = valid_manifest()
    manifest["version"] = "1.2.3"
    import yaml
    raw_manifest = yaml.safe_dump(manifest).encode()
    requests = []

    def fake_json(url):
        requests.append(url)
        if url.endswith("/commits/main"):
            return {"sha": sha}
        if url.endswith(f"/git/trees/{sha}?recursive=1"):
            return {
                "truncated": False,
                "tree": [
                    {"path": path, "type": "blob"}
                    for paths in manifest["active_files"].values()
                    for path in paths
                ] + [
                    {"path": "VERSION", "type": "blob"},
                    {"path": "tools/tsar-cli/pyproject.toml", "type": "blob"},
                ],
            }
        raise AssertionError(f"Unexpected JSON URL: {url}")

    def fake_bytes(url, **_kwargs):
        requests.append(url)
        if url.endswith(f"/{sha}/manifest.yaml"):
            return raw_manifest
        if url.endswith(f"/{sha}/VERSION"):
            return b"1.2.3\n"
        if url.endswith(f"/{sha}/tools/tsar-cli/pyproject.toml"):
            return b'[project]\nversion = "1.2.3"\n'
        if f"/{sha}/" in url:
            return b"# policy\n"
        raise AssertionError(f"Unexpected byte URL: {url}")

    monkeypatch.setattr(verifier, "fetch_json", fake_json)
    monkeypatch.setattr(verifier, "fetch_bytes", fake_bytes)
    monkeypatch.setattr("sys.argv", ["verify_upstream.py", "--domain", "ai_security",
                                     "--report", str(tmp_path / "report.json")])

    assert verifier.main() == 0
    report = __import__("json").loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["commit_sha"] == sha
    assert report["selected_domains"] == ["core", "ai_security"]
    assert set(report["core_files_read"]) == verifier.REQUIRED_CORE
    assert all(f"/{sha}/" in url for url in requests if "/raw.githubusercontent.com/" in url)


def test_main_fails_closed_for_unknown_domain(monkeypatch):
    sha = "b" * 40
    manifest = valid_manifest()
    import yaml

    def fake_json(url):
        if url.endswith("/commits/main"):
            return {"sha": sha}
        return {
            "truncated": False,
            "tree": [
                {"path": path, "type": "blob"}
                for paths in manifest["active_files"].values()
                for path in paths
            ] + [
                {"path": "VERSION", "type": "blob"},
                {"path": "tools/tsar-cli/pyproject.toml", "type": "blob"},
            ],
        }

    def fake_bytes(url, **_kwargs):
        if url.endswith(f"/{sha}/manifest.yaml"):
            return yaml.safe_dump(manifest).encode()
        if url.endswith(f"/{sha}/VERSION"):
            return b"1.2.3\\n"
        if url.endswith(f"/{sha}/tools/tsar-cli/pyproject.toml"):
            return b'[project]\\nversion = "1.2.3"\\n'
        return b"# policy\\n"

    monkeypatch.setattr(verifier, "fetch_json", fake_json)
    monkeypatch.setattr(verifier, "fetch_bytes", fake_bytes)
    monkeypatch.setattr("sys.argv", ["verify_upstream.py", "--domain", "not_a_real_domain"])

    assert verifier.main() == 2
