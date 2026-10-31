#!/usr/bin/env python3
"""TSAR crypto inventory: detect algorithms in code."""
import re
import sys
import json
from pathlib import Path

ALGOS = {
    "AES-GCM": re.compile(r"AES[-_]?GCM", re.I),
    "AES-CBC": re.compile(r"AES[-_]?CBC", re.I),
    "AES-ECB": re.compile(r"AES[-_]?ECB|ECB", re.I),
    "ChaCha20-Poly1305": re.compile(r"ChaCha20[-_]?Poly1305|XChaCha20", re.I),
    "RSA": re.compile(r"\bRSA\b", re.I),
    "ECDSA": re.compile(r"\bECDSA\b", re.I),
    "Ed25519": re.compile(r"\bEd25519\b", re.I),
    "ML-KEM": re.compile(r"ML[-_]?KEM|Kyber", re.I),
    "ML-DSA": re.compile(r"ML[-_]?DSA|Dilithium", re.I),
    "Argon2": re.compile(r"\bArgon2(id)?\b", re.I),
    "bcrypt": re.compile(r"\bbcrypt\b", re.I),
    "scrypt": re.compile(r"\bscrypt\b", re.I),
    "PBKDF2": re.compile(r"\bPBKDF2\b", re.I),
    "SHA-1": re.compile(r"SHA[-_]?1\b", re.I),
    "SHA-256": re.compile(r"SHA[-_]?256\b", re.I),
    "MD5": re.compile(r"\bMD5\b", re.I),
}

RISKY = {"AES-ECB", "SHA-1", "MD5", "AES-CBC"}

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".venv", "__pycache__"}

def inventory(path: Path):
    found = {}
    for f in path.rglob("*"):
        if not f.is_file() or f.stat().st_size > 2_000_000:
            continue
        if any(part in SKIP_DIRS for part in f.parts):
            continue
        try:
            text = f.read_text(errors="ignore")
        except Exception:
            continue
        for algo, pat in ALGOS.items():
            for m in pat.finditer(text):
                line = text[:m.start()].count("\n") + 1
                found.setdefault(algo, []).append(f"{f}:{line}")
    return found

def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    found = inventory(target)
    report = {
        "algorithms": {k: {"count": len(v), "locations": v[:10]} for k, v in found.items()},
        "risky": [a for a in found if a in RISKY],
        "missing_pq": "ML-KEM" not in found and "ML-DSA" not in found,
    }
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
