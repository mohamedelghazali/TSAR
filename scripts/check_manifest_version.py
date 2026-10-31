#!/usr/bin/env python3
"""Compare local manifest version against remote."""
import sys
import urllib.request
import re
from pathlib import Path

def main():
    p = Path(__file__).resolve().parent.parent / "manifest.yaml"
    local = re.search(r'version:\s*"([\d.]+)"', p.read_text()).group(1)
    url = re.search(r'check_url:\s*"([^"]+)"', p.read_text()).group(1)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TSAR-Check/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            remote = re.search(r'version:\s*"([\d.]+)"', resp.read().decode()).group(1)
    except Exception as e:
        print(f"WARN: cannot reach remote manifest: {e}")
        sys.exit(2)
    if remote != local:
        print(f"UPDATE: local={local} remote={remote}")
        sys.exit(1)
    print(f"OK: version {local}")

if __name__ == "__main__":
    main()
