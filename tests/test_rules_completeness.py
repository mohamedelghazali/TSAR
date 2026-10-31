"""Verify every rule domain is covered in manifest and examples."""
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

REQUIRED_DOMAINS = [
    "core", "crypto", "ai_security", "owasp_web",
    "platform", "hardware", "data",
]

REQUIRED_LANGUAGES = ["python", "node", "go", "rust", "java", "kotlin", "swift"]

def test_manifest_has_all_domains():
    data = yaml.safe_load((ROOT / "manifest.yaml").read_text())
    for domain in REQUIRED_DOMAINS:
        assert domain in data["active_files"], f"missing domain: {domain}"
        assert data["active_files"][domain], f"empty domain: {domain}"

def test_all_referenced_files_exist():
    data = yaml.safe_load((ROOT / "manifest.yaml").read_text())
    for group, files in data["active_files"].items():
        for rel in files:
            assert (ROOT / rel).exists(), f"missing: {rel}"

def test_examples_present_for_all_languages():
    base = ROOT / "examples" / "secure"
    for lang in REQUIRED_LANGUAGES:
        assert (base / lang).exists(), f"missing example: {lang}"

def test_rules_have_controls_section():
    for path in (ROOT / "rules").rglob("*.md"):
        text = path.read_text()
        assert "## " in text, f"{path} has no section"
        assert len(text) > 200, f"{path} too short"

def test_blockchain_rules_present():
    base = ROOT / "rules" / "blockchain"
    for name in ["solidity.md", "solana.md", "wallet-integration.md"]:
        assert (base / name).exists()
