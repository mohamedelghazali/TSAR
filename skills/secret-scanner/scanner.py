#!/usr/bin/env python3
"""TSAR secret scanner. Blocks output on detection."""
import re
import sys
import math
from pathlib import Path

PATTERNS = {
    "aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "openai_key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "anthropic_key": re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    "github_token": re.compile(r"ghp_[A-Za-z0-9]{36}"),
    "google_api": re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    "stripe_key": re.compile(r"sk_live_[0-9a-zA-Z]{24,}"),
    "private_key": re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "db_url": re.compile(r"\w+://[^:\s]+:[^@\s]+@"),
    "jwt": re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
}

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".venv", "__pycache__"}

def entropy(s: str) -> float:
    if not s:
        return 0.0
    return -sum((s.count(c) / len(s)) * math.log2(s.count(c) / len(s)) for c in set(s))

def scan(path: Path):
    findings = []
    for f in path.rglob("*"):
        if not f.is_file() or f.stat().st_size > 2_000_000:
            continue
        if any(part in SKIP_DIRS for part in f.parts):
            continue
        try:
            text = f.read_text(errors="ignore")
        except Exception:
            continue
        for name, pat in PATTERNS.items():
            for m in pat.finditer(text):
                line = text[:m.start()].count("\n") + 1
                findings.append((f, line, name))
        for line_no, line in enumerate(text.splitlines(), 1):
            for word in re.findall(r"[A-Za-z0-9+/=_-]{32,}", line):
                if entropy(word) > 4.5:
                    findings.append((f, line_no, "high_entropy"))
    return findings

def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    hits = scan(target)
    if hits:
        for f, ln, kind in hits:
            print(f"BLOCK: {f}:{ln} [{kind}]")
        sys.exit(1)
    print("OK: no secrets detected")

if __name__ == "__main__":
    main()
