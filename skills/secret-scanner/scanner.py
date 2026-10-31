#!/usr/bin/env python3
"""TSAR secret scanner. Blocks on detected credentials without skipping test/example trees."""
import math
import re
import sys
from pathlib import Path

PATTERNS = {
    "aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "openai_key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "anthropic_key": re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    "github_token": re.compile(r"ghp_[A-Za-z0-9]{36}"),
    "google_api": re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    "stripe_key": re.compile(r"sk_live_[0-9a-zA-Z]{24,}"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "db_url": re.compile(r"\w+://[^:\s]+:[^@\s]+@"),
    "jwt": re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
}
SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".venv", "__pycache__"}
URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
TOKEN_RE = re.compile(r"[A-Za-z0-9+/=_-]{32,}")
SECRET_CONTEXT_RE = re.compile(r"(?i)(secret|token|api[_-]?key|password|credential|authorization)\s*[:=]")

def entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {char: value.count(char) for char in set(value)}
    return -sum((count / len(value)) * math.log2(count / len(value)) for count in counts.values())

def _files(path: Path):
    if path.is_file():
        return [path]
    return (item for item in path.rglob("*") if item.is_file())

def _is_known_test_fixture(path: Path, line: str) -> bool:
    # Suppress only documented dummy literals in test source files; never skip a whole directory.
    return (
        "tests" in path.parts
        and path.name.startswith("test_")
        and (DUMMY_AWS_TEST_VALUE in line or DUMMY_PEM_HEADER in line and "AAAA" in line)
    )

def scan(path: Path):
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

        lines = content.splitlines()
        for name, pattern in PATTERNS.items():
            for match in pattern.finditer(content):
                line_no = content.count("\n", 0, match.start()) + 1
                line = lines[line_no - 1] if line_no <= len(lines) else ""
                if _is_known_test_fixture(file_path, line):
                    continue
                # A PEM marker in tests is ignored only when it is the explicit AAAA fixture above.
                findings.append((file_path, line_no, name))

        for line_no, line in enumerate(lines, 1):
            if _is_known_test_fixture(file_path, line):
                continue
            # URL query strings are not entropy-scanned; credential patterns above still inspect them.
            without_urls = URL_RE.sub(" ", line)
            if not SECRET_CONTEXT_RE.search(without_urls):
                continue
            for candidate in TOKEN_RE.findall(without_urls):
                if entropy(candidate) >= 4.5:
                    findings.append((file_path, line_no, "high_entropy"))
    return findings

def main() -> int:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".").expanduser()
    if not target.exists():
        print(f"ERROR: path does not exist: {target}", file=sys.stderr)
        return 2
    if not (target.is_file() or target.is_dir()):
        print(f"ERROR: path is not a regular file or directory: {target}", file=sys.stderr)
        return 2
    hits = scan(target)
    if hits:
        for file_path, line_no, kind in hits:
            print(f"BLOCK: {file_path}:{line_no} [{kind}]")
        return 1
    print("OK: no secrets detected")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
