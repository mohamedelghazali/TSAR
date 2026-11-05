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
