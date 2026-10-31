#!/usr/bin/env python3
"""Fetch upstream security standards and stage diffs for review."""
import sys
import hashlib
import urllib.request
from pathlib import Path

UPSTREAM = {
    "owasp-llm": "https://raw.githubusercontent.com/OWASP/www-project-top-10-for-large-language-model-applications/main/README.md",
    "nist-ai-rmf": "https://raw.githubusercontent.com/usnistgov/AIRMF/main/README.md",
    "cwe-top25": "https://raw.githubusercontent.com/OWASP/Top10/master/README.md",
}

CACHE_DIR = Path(".tsar-cache")
CACHE_DIR.mkdir(exist_ok=True)

def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "TSAR-Sync/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()

def main():
    changed = []
    for name, url in UPSTREAM.items():
        try:
            data = fetch(url)
        except Exception as e:
            print(f"WARN: fetch failed for {name}: {e}")
            continue
        digest = hashlib.sha256(data).hexdigest()
        marker = CACHE_DIR / f"{name}.sha256"
        prev = marker.read_text().strip() if marker.exists() else ""
        if digest != prev:
            marker.write_text(digest)
            changed.append(name)
    if changed:
        print("Upstream changed: " + ", ".join(changed))
        print("Review diffs and update rules manually before merging.")
    else:
        print("Upstream unchanged")

if __name__ == "__main__":
    main()
