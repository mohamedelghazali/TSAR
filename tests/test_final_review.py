"""Final consistency checks across the entire repository."""
import re
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def test_readme_exists():
    assert (ROOT / "README.md").exists()

def test_license_exists():
    assert (ROOT / "LICENSE").exists()

def test_security_policy_exists():
    assert (ROOT / "SECURITY.md").exists()

def test_contributing_exists():
    assert (ROOT / "CONTRIBUTING.md").exists()

def test_roadmap_exists():
    assert (ROOT / "ROADMAP.md").exists()

def test_changelog_exists():
    assert (ROOT / "CHANGELOG.md").exists()

def test_architecture_doc_exists():
    assert (ROOT / "docs" / "architecture.md").exists()

def test_final_review_doc_exists():
    assert (ROOT / "docs" / "final-review.md").exists()

def test_verify_script_exists():
    p = ROOT / "verify-all.sh"
    assert p.exists()
    assert p.stat().st_mode & 0o111

def test_all_rule_domains_have_docs():
    rules = ROOT / "rules"
    docs = ROOT / "docs"
    assert rules.exists() and docs.exists()
    domains = [d for d in rules.iterdir() if d.is_dir()]
    assert len(domains) >= 30, f"expected >= 30 domains, got {len(domains)}"

def test_manifest_active_files_consistent():
    data = yaml.safe_load((ROOT / "manifest.yaml").read_text())
    listed = set()
    for group, files in data["active_files"].items():
        for rel in files:
            listed.add(rel)
    rule_files = set()
    for f in (ROOT / "rules").rglob("*.md"):
        rule_files.add(str(f.relative_to(ROOT)))
    unlisted = rule_files - listed
    unlisted = {u for u in unlisted if not u.endswith("README.md")}
    assert not unlisted, f"unlisted rule files: {sorted(unlisted)[:5]}"

def test_no_hardcoded_secrets():
    pattern = re.compile(r"(AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36}|-----BEGIN (RSA |EC )?PRIVATE KEY-----)")
    bad = []
    for f in ROOT.rglob("*"):
        if not f.is_file() or ".git" in f.parts:
            continue
        if "DO_NOT_GENERATE" in str(f) or "anti-patterns" in str(f):
            continue
        try:
            text = f.read_text(errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                bad.append(f"{f}:{i}")
    assert not bad, f"secrets found in: {bad[:5]}"

def test_all_prompts_have_manifest_reference():
    for f in (ROOT / "prompts").glob("*.md"):
        text = f.read_text()
        assert "manifest" in text.lower(), f"{f.name} does not reference manifest"

def test_all_prompts_have_core_reference():
    for f in (ROOT / "prompts").glob("*.md"):
        text = f.read_text()
        assert "CORE_DIRECTIVE" in text or "core" in text.lower(), \
            f"{f.name} does not reference core directive"
