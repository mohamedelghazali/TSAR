---
name: crypto-inventory
description: Build a cryptographic bill of materials for a repository by identifying cryptographic algorithms, key sizes, libraries, certificates, and deprecated or risky cryptographic usage. Use when auditing cryptography, planning post-quantum migration, or reviewing cryptographic dependencies.
---

# Crypto Inventory Skill

## Purpose
Build a Cryptographic Bill of Materials (CBOM) for a repository.

## Invocation
`python skills/crypto-inventory/inventory.py <path>`

## Output
- Algorithms detected (with file:line).
- Key sizes.
- Libraries in use.
- Risk flags for deprecated algorithms.
- Migration notes toward PQC.

## Format
JSON (machine-readable) and Markdown (human-readable).
