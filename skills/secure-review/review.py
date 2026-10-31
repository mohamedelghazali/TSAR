#!/usr/bin/env python3
"""TSAR static review. Blocks output on high-severity findings."""
import re
import sys
from pathlib import Path

PATTERNS = [
    ("sql_injection", re.compile(r"(execute|query|raw)\s*\(\s*[f\"'].*(\+|\{).*\)"), "HIGH", "Use parameterized queries."),
    ("command_injection", re.compile(r"(execSync|system|popen|subprocess\.call)\s*\([^)]*\+"), "HIGH", "Use argument arrays, never shell string concat."),
    ("eval_usage", re.compile(r"\beval\s*\("), "HIGH", "Remove eval; use a parser."),
    ("pickle_load", re.compile(r"pickle\.loads?\s*\("), "HIGH", "Never unpickle untrusted data."),
    ("yaml_unsafe", re.compile(r"yaml\.load\s*\([^,)]*\)"), "HIGH", "Use yaml.safe_load."),
    ("innerhtml", re.compile(r"\.innerHTML\s*=\s*[^;]+"), "HIGH", "Use textContent or sanitize with DOMPurify."),
    ("dangerous_html", re.compile(r"dangerouslySetInnerHTML"), "HIGH", "Sanitize before injection."),
    ("ssrf", re.compile(r"(requests\.get|fetch|axios\.get)\s*\(\s*(req\.|request\.|params\.)"), "HIGH", "Validate URL against allow-list."),
    ("path_traversal", re.compile(r"open\s*\([^)]*(\+|\{)[^)]*\)"), "MEDIUM", "Resolve and validate against base directory."),
    ("tls_disabled", re.compile(r"(verify\s*=\s*False|InsecureSkipVerify\s*:\s*true|rejectUnauthorized\s*:\s*false)"), "HIGH", "Enable certificate verification."),
    ("weak_crypto", re.compile(r"\b(MD5|SHA1|DES|RC4|ECB)\b"), "HIGH", "Use AES-256-GCM, SHA-256+."),
    ("weak_random", re.compile(r"\b(Math\.random|random\.random|rand\(\))\b"), "MEDIUM", "Use CSPRNG for security values."),
]
SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".venv", "__pycache__"}

def _files(path: Path):
    if path.is_file():
        return [path]
    return (item for item in path.rglob("*") if item.is_file())

def review(path: Path):
    findings = []
    for file_path in _files(path):
        if any(part in SKIP_DIRS for part in file_path.parts):
            continue
        try:
            if file_path.stat().st_size > 2_000_000:
                continue
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeError):
            continue
        for name, pattern, severity, hint in PATTERNS:
            for match in pattern.finditer(content):
                line_no = content.count("\n", 0, match.start()) + 1
                findings.append((file_path, line_no, name, severity, hint))
    return findings

def main() -> int:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".").expanduser()
    if not target.exists():
        print(f"ERROR: path does not exist: {target}", file=sys.stderr)
        return 2
    if not (target.is_file() or target.is_dir()):
        print(f"ERROR: path is not a regular file or directory: {target}", file=sys.stderr)
        return 2
    hits = review(target)
    high = [finding for finding in hits if finding[3] == "HIGH"]
    for file_path, line_no, name, severity, hint in hits:
        print(f"{severity}: {file_path}:{line_no} [{name}] {hint}")
    if high:
        return 1
    print(f"OK: {len(hits)} low/medium findings, no blockers")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
