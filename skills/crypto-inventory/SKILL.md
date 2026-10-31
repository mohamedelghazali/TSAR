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
