"""Unit tests for TSAR upstream preflight manifest validation."""
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("verify_upstream.py")
SPEC = importlib.util.spec_from_file_location("verify_upstream", MODULE_PATH)
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
        "enforcement": {
            "default_mode": "strict",
            "allow_advisory_fallback": False,
        },
        "active_files": {
            "core": sorted(verifier.REQUIRED_CORE),
            "ai_security": ["rules/owasp-llm/llm01-prompt-injection.md"],
        },
    }


class ManifestValidationTests(unittest.TestCase):
    def test_accepts_valid_strict_manifest(self):
        version, groups = verifier.validate_manifest(valid_manifest())
        self.assertEqual(version, "1.2.3")
        self.assertEqual(set(groups["core"]), verifier.REQUIRED_CORE)

    def test_rejects_wrong_repository_identity(self):
        manifest = valid_manifest()
        manifest["repository"] = "https://example.com/TSAR"
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_manifest(manifest)

    def test_rejects_non_fail_closed_configuration(self):
        manifest = valid_manifest()
        manifest["lifecycle"]["fail_closed"] = False
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_manifest(manifest)

    def test_rejects_advisory_fallback(self):
        manifest = valid_manifest()
        manifest["enforcement"]["allow_advisory_fallback"] = True
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_manifest(manifest)

    def test_rejects_missing_core_policy(self):
        manifest = valid_manifest()
        manifest["active_files"]["core"].remove("system/LIFECYCLE.md")
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_manifest(manifest)

    def test_rejects_path_traversal(self):
        manifest = valid_manifest()
        manifest["active_files"]["ai_security"] = ["rules/../secrets.md"]
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_manifest(manifest)

    def test_rejects_duplicate_active_path(self):
        manifest = valid_manifest()
        manifest["active_files"]["ai_security"] = ["system/LIFECYCLE.md"]
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_manifest(manifest)

    def test_rejects_invalid_semver(self):
        manifest = valid_manifest()
        manifest["version"] = "latest"
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
