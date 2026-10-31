#!/usr/bin/env python3
"""Fail if any rule, prompt, or doc file is empty or trivial."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK_DIRS = ["rules", "prompts", "system", "skills", "docs", "integrations"]
MIN_BYTES = 200
MIN_LINES = 5

def main() -> int:
    bad = []
    for d in CHECK_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for f in base.rglob("*.md"):
            if f.stat().st_size < MIN_BYTES:
                bad.append((f, f"{f.stat().st_size} bytes"))
                continue
            text = f.read_text(errors="ignore")
            if len([l for l in text.splitlines() if l.strip()]) < MIN_LINES:
                bad.append((f, f"{len(text.splitlines())} lines"))
        for f in base.rglob("*.yml"):
            if f.stat().st_size < MIN_BYTES:
                bad.append((f, f"{f.stat().st_size} bytes"))
        for f in base.rglob("*.yaml"):
            if f.stat().st_size < MIN_BYTES:
                bad.append((f, f"{f.stat().st_size} bytes"))
    if bad:
        print("Empty or trivial files:")
        for f, reason in bad:
            print(f"  - {f.relative_to(ROOT)} ({reason})")
        return 1
    print(f"OK: all files in {CHECK_DIRS} are non-trivial")
    return 0

if __name__ == "__main__":
    sys.exit(main())
