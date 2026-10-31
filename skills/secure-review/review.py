#!/usr/bin/env python3
"""TSAR static review. Blocks output on high-severity findings."""
import re
import sys
from pathlib import Path

PATTERNS = [
    ("sql_injection", re.compile(r"(execute|query|raw)\s*\(\s*[f\"'].*(\+|\{).*\)"), "HIGH",
     "Use parameterized queries."),
    ("command_injection", re.compile(r"(execSync|system|popen|subprocess\.call)\s*\([^)]*\+"), "HIGH",
     "Use argument arrays, never shell string concat."),
    ("eval_usage", re.compile(r"\beval\s*\("), "HIGH",
     "Remove eval; use a parser."),
    ("pickle_load", re.compile(r"pickle\.loads?\s*\("), "HIGH",
     "Never unpickle untrusted data."),
    ("yaml_unsafe", re.compile(r"yaml\.load\s*\([^,)]*\)"), "HIGH",
     "Use yaml.safe_load."),
    ("innerhtml", re.compile(r"\.innerHTML\s*=\s*[^;]+"), "HIGH",
     "Use textContent or sanitize with DOMPurify."),
    ("dangerous_html", re.compile(r"dangerouslySetInnerHTML"), "HIGH",
     "Sanitize before injection."),
    ("ssrf", re.compile(r"(requests\.get|fetch|axios\.get)\s*\(\s*(req\.|request\.|params\.)"), "HIGH",
     "Validate URL against allow-list."),
    ("path_traversal", re.compile(r"open\s*\([^)]*(\+|\{)[^)]*\)"), "MEDIUM",
     "Resolve and validate against base directory."),
    ("tls_disabled", re.compile(r"(verify\s*=\s*False|InsecureSkipVerify\s*:\s*true|rejectUnauthorized\s*:\s*false)"), "HIGH",
     "Enable certificate verification."),
    ("weak_crypto", re.compile(r"\b(MD5|SHA1|DES|RC4|ECB)\b"), "HIGH",
     "Use AES-256-GCM, SHA-256+."),
    ("weak_random", re.compile(r"\b(Math\.random|random\.random|rand\(\))\b"), "MEDIUM",
     "Use CSPRNG for security values."),
]

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".venv", "__pycache__"}

def review(path: Path):
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
        for name, pat, sev, hint in PATTERNS:
            for m in pat.finditer(text):
                line = text[:m.start()].count("\n") + 1
                findings.append((f, line, name, sev, hint))
    return findings

def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    hits = review(target)
    high = [h for h in hits if h[3] == "HIGH"]
    for f, ln, name, sev, hint in hits:
        print(f"{sev}: {f}:{ln} [{name}] {hint}")
    if high:
        sys.exit(1)
    print(f"OK: {len(hits)} low/medium findings, no blockers")

if __name__ == "__main__":
    main()
