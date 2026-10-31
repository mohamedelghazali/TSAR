#!/usr/bin/env python3
"""Validate TSAR rules: manifest integrity, cross-references, and versioning."""
import os
import re
import sys
import yaml
from pathlib import Path

REQUIRED_SECTIONS = {
    "system/CORE_DIRECTIVE.md": ["Pre-Flight Protocol", "Absolute Prohibitions", "Mandatory Patterns"],
    "system/DO_NOT_GENERATE.md": ["Secrets", "Cryptography", "Injection"],
    "rules/crypto/algorithms.md": ["Symmetric", "Password Hashing", "Key Exchange", "Randomness", "TLS"],
    "rules/crypto/post-quantum.md": ["ML-KEM", "ML-DSA"],
}

def check_manifest(root: Path) -> list:
    errors = []
    mf = root / "manifest.yaml"
    if not mf.exists():
        return ["manifest.yaml missing"]
    data = yaml.safe_load(mf.read_text())
    for key in ("version", "active_files", "lifecycle", "enforcement"):
        if key not in data:
            errors.append(f"manifest missing key: {key}")
    for group, files in data.get("active_files", {}).items():
        for rel in files:
            if not (root / rel).exists():
                errors.append(f"manifest references missing file: {rel}")
    version = data.get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append(f"invalid semver: {version}")
    return errors

def check_required_sections(root: Path) -> list:
    errors = []
    for rel, sections in REQUIRED_SECTIONS.items():
        p = root / rel
        if not p.exists():
            errors.append(f"required file missing: {rel}")
            continue
        text = p.read_text()
        for s in sections:
            if s.lower() not in text.lower():
                errors.append(f"{rel} missing section: {s}")
    return errors

def check_no_hardcoded_secrets(root: Path) -> list:
    errors = []
    pat = re.compile(r"(AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36}|-----BEGIN (RSA |EC )?PRIVATE KEY-----)")
    for f in root.rglob("*.md"):
        if ".git" in f.parts:
            continue
        for i, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
            if pat.search(line) and "DO_NOT_GENERATE" not in str(f):
                errors.append(f"{f}:{i} contains a secret-like string")
    return errors

def main():
    root = Path(__file__).resolve().parent.parent
    errors = []
    errors += check_manifest(root)
    errors += check_required_sections(root)
    errors += check_no_hardcoded_secrets(root)
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print("OK: TSAR rules valid")

if __name__ == "__main__":
    main()
