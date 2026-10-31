#!/usr/bin/env python3
"""TSAR threat modeler: STRIDE skeleton from a description."""
import sys
from pathlib import Path

STRIDE = {
    "Spoofing": "Enforce strong authentication; mTLS for services; Ed25519/ML-DSA signatures.",
    "Tampering": "AEAD encryption; signed messages; integrity via HMAC-SHA-256.",
    "Repudiation": "Tamper-evident audit log with hash chain; sign events.",
    "Information Disclosure": "Encrypt at rest and in transit; redact logs; least privilege.",
    "Denial of Service": "Rate limits; quotas; circuit breakers; input size caps.",
    "Elevation of Privilege": "Least privilege; short-lived tokens; human confirmation for admin actions.",
}

def main():
    if len(sys.argv) < 2:
        print("Usage: model.py <description.txt>")
        sys.exit(2)
    desc = Path(sys.argv[1]).read_text(errors="ignore")
    print("# Threat Model (STRIDE)\n")
    print("## Input Summary\n")
    print(desc.strip()[:500] + ("\n..." if len(desc) > 500 else ""))
    print("\n## Threats and Mitigations\n")
    for category, mitigation in STRIDE.items():
        print(f"### {category}\n- Mitigation: {mitigation}\n")

if __name__ == "__main__":
    main()
