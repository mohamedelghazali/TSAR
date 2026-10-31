#!/usr/bin/env python3
"""Fetch upstream standards and atomically stage fingerprint changes for review."""
from __future__ import annotations

import hashlib
import os
import shutil
import sys
import tempfile
import urllib.request
import uuid
from pathlib import Path

UPSTREAM = {
    "owasp-llm": "https://raw.githubusercontent.com/OWASP/www-project-top-10-for-large-language-model-applications/main/README.md",
    "nist-ai-rmf": "https://raw.githubusercontent.com/usnistgov/AIRMF/main/README.md",
    "owasp-top10": "https://raw.githubusercontent.com/OWASP/Top10/master/README.md",
}

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / ".tsar-cache"
MAX_SOURCE_BYTES = 5 * 1024 * 1024


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "TSAR-Standards-Sync/2.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(MAX_SOURCE_BYTES + 1)
    if not data:
        raise ValueError("upstream returned an empty response")
    if len(data) > MAX_SOURCE_BYTES:
        raise ValueError(f"upstream response exceeds {MAX_SOURCE_BYTES} bytes")
    return data


def recover_interrupted_cache() -> None:
    """Restore the newest backup if a prior process stopped between directory swaps."""
    if CACHE_DIR.exists() or CACHE_DIR.is_symlink():
        return
    backups = sorted(
        CACHE_DIR.parent.glob(f"{CACHE_DIR.name}.backup.*"),
        key=lambda path: path.name,
        reverse=True,
    )
    if backups:
        os.replace(backups[0], CACHE_DIR)
        print(f"Recovered interrupted cache update from {backups[0].name}")


def read_previous_digest(name: str) -> str:
    marker = CACHE_DIR / f"{name}.sha256"
    if not marker.is_file():
        return ""
    value = marker.read_text(encoding="ascii").strip()
    if len(value) != 64 or any(char not in "0123456789abcdef" for char in value.lower()):
        raise ValueError(f"invalid SHA-256 cache marker: {marker}")
    return value.lower()


def commit_cache_atomically(digests: dict[str, str]) -> None:
    """Replace the complete cache directory, restoring it if promotion fails."""
    parent = CACHE_DIR.parent
    if CACHE_DIR.is_symlink() or (CACHE_DIR.exists() and not CACHE_DIR.is_dir()):
        raise RuntimeError(f"cache path is not a directory: {CACHE_DIR}")

    stage = Path(tempfile.mkdtemp(prefix=f"{CACHE_DIR.name}.stage.", dir=parent))
    backup = parent / f"{CACHE_DIR.name}.backup.{os.getpid()}.{uuid.uuid4().hex}"
    old_moved = False
    try:
        if CACHE_DIR.is_dir():
            for child in CACHE_DIR.iterdir():
                destination = stage / child.name
                if child.is_dir() and not child.is_symlink():
                    shutil.copytree(child, destination, symlinks=True)
                elif child.is_symlink():
                    destination.symlink_to(os.readlink(child), target_is_directory=child.is_dir())
                else:
                    shutil.copy2(child, destination)

        # Remove obsolete managed markers only after all sources were fetched.
        expected = {f"{name}.sha256" for name in UPSTREAM}
        for marker in stage.glob("*.sha256"):
            if marker.name not in expected:
                marker.unlink()

        for name, digest in digests.items():
            temporary = stage / f".{name}.sha256.tmp"
            temporary.write_text(digest + "\n", encoding="ascii")
            os.replace(temporary, stage / f"{name}.sha256")

        if CACHE_DIR.exists():
            os.replace(CACHE_DIR, backup)
            old_moved = True
        try:
            os.replace(stage, CACHE_DIR)
        except Exception:
            if old_moved and backup.exists() and not CACHE_DIR.exists():
                os.replace(backup, CACHE_DIR)
            raise
    finally:
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)

    if backup.exists():
        shutil.rmtree(backup)


def main() -> int:
    try:
        recover_interrupted_cache()
        if CACHE_DIR.is_symlink():
            raise RuntimeError(f"refusing symlink cache path: {CACHE_DIR}")

        # Fetch and validate every source before reading or writing cache state.
        fetched: dict[str, bytes] = {}
        for name, url in UPSTREAM.items():
            try:
                fetched[name] = fetch(url)
            except Exception as exc:
                print(f"FATAL: failed to fetch {name}: {exc}", file=sys.stderr)
                print("Synchronization aborted; cache was not changed.", file=sys.stderr)
                return 1

        digests = {
            name: hashlib.sha256(data).hexdigest()
            for name, data in fetched.items()
        }
        changed = [
            name for name, digest in digests.items()
            if digest != read_previous_digest(name)
        ]

        if not changed:
            print("Upstream sources unchanged; cache and manifest were not modified.")
            return 0

        print("Upstream changes detected: " + ", ".join(changed))
        commit_cache_atomically(digests)
        print(
            "Fingerprint cache updated atomically. Review upstream content and "
            "update TSAR rules manually before merging."
        )
        return 0
    except Exception as exc:
        print(f"FATAL: synchronization aborted: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
