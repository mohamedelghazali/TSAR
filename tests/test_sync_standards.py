"""Fail-closed tests for upstream standards synchronization."""
import hashlib
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_standards.py"


def load_sync_module():
    spec = importlib.util.spec_from_file_location("tsar_sync_standards_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_fetch_failure_does_not_modify_existing_cache(tmp_path, monkeypatch):
    module = load_sync_module()
    cache = tmp_path / ".tsar-cache"
    cache.mkdir()
    marker = cache / "old.sha256"
    marker.write_text("previous marker", encoding="ascii")
    note = cache / "operator-note.txt"
    note.write_text("keep", encoding="utf-8")
    monkeypatch.setattr(module, "CACHE_DIR", cache)
    monkeypatch.setattr(module, "UPSTREAM", {"first": "url-1", "second": "url-2"})

    def fake_fetch(url):
        if url == "url-2":
            raise OSError("simulated upstream outage")
        return b"new upstream content"

    monkeypatch.setattr(module, "fetch", fake_fetch)
    assert module.main() == 1
    assert marker.read_text(encoding="ascii") == "previous marker"
    assert note.read_text(encoding="utf-8") == "keep"


def test_changed_sources_are_reported_after_atomic_cache_update(tmp_path, monkeypatch):
    module = load_sync_module()
    cache = tmp_path / ".tsar-cache"
    output = tmp_path / "github-output.txt"
    monkeypatch.setattr(module, "CACHE_DIR", cache)
    monkeypatch.setattr(module, "UPSTREAM", {"owasp": "url-1", "nist": "url-2"})
    monkeypatch.setattr(module, "fetch", lambda _url: b"new standards")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    assert module.main() == 0
    expected = hashlib.sha256(b"new standards").hexdigest()
    assert (cache / "owasp.sha256").read_text(encoding="ascii").strip() == expected
    assert (cache / "nist.sha256").is_file()
    values = output.read_text(encoding="utf-8")
    assert "changed=true" in values
    assert "changed_sources=owasp,nist" in values


def test_unchanged_sources_report_false_without_replacing_cache(tmp_path, monkeypatch):
    module = load_sync_module()
    cache = tmp_path / ".tsar-cache"
    cache.mkdir()
    digest = hashlib.sha256(b"same").hexdigest()
    for name in ("owasp", "nist"):
        (cache / f"{name}.sha256").write_text(digest + "\n", encoding="ascii")
    output = tmp_path / "github-output.txt"
    monkeypatch.setattr(module, "CACHE_DIR", cache)
    monkeypatch.setattr(module, "UPSTREAM", {"owasp": "url-1", "nist": "url-2"})
    monkeypatch.setattr(module, "fetch", lambda _url: b"same")
    monkeypatch.setattr(
        module, "commit_cache_atomically",
        lambda _digests: (_ for _ in ()).throw(AssertionError("cache must not be replaced")),
    )
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    assert module.main() == 0
    assert "changed=false" in output.read_text(encoding="utf-8")
