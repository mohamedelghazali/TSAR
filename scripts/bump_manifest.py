#!/usr/bin/env python3
"""Increment patch version in manifest.yaml."""
import re
import sys
from pathlib import Path

def main():
    p = Path(__file__).resolve().parent.parent / "manifest.yaml"
    text = p.read_text()
    m = re.search(r'version:\s*"([0-9]+)\.([0-9]+)\.([0-9]+)"', text)
    if not m:
        print("FAIL: version not found")
        sys.exit(1)
    major, minor, patch = map(int, m.groups())
    new = f"{major}.{minor}.{patch + 1}"
    text = text.replace(m.group(0), f'version: "{new}"')
    p.write_text(text)
    print(f"Bumped to {new}")

if __name__ == "__main__":
    main()
