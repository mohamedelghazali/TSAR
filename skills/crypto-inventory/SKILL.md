---
name: crypto-inventory
description: Run a lightweight, pattern-based inventory of cryptographic algorithm references in a repository. Reports algorithm counts, up to ten file-and-line locations per algorithm, a shortlist of algorithms flagged for review, and whether ML-KEM or ML-DSA references were detected. It does not inspect runtime behavior, determine key sizes, identify cryptographic libraries or certificates, or produce a complete CBOM.
---

# Crypto Inventory Skill

## Purpose
Provide a lightweight static-text inventory of cryptographic algorithm references to help reviewers locate areas for further examination. This is a heuristic inventory, not a complete Cryptographic Bill of Materials (CBOM) and not proof that an algorithm is used securely or at runtime.

## Invocation
`python skills/crypto-inventory/inventory.py <repository-directory>`

Pass a repository directory. The current script recursively scans readable files up to 2 MB and skips common generated/vendor directories.

## Output
The script prints JSON containing:
- `algorithms`: detected algorithm names, occurrence counts, and up to ten `file:line` locations for each algorithm.
- `risky`: detected references to AES-ECB, AES-CBC, SHA-1, or MD5. These are review flags, not automatic proof of exploitable vulnerabilities; assess the context and intended use.
- `missing_pq`: `true` when neither ML-KEM nor ML-DSA references are detected by the current patterns; this is not proof that the system lacks post-quantum protection.

## Limitations
- Pattern matching can produce false positives and false negatives.
- The tool does not determine key sizes, inspect key material, identify libraries or certificates, validate algorithm parameters, trace data flows, or establish runtime use.
- It does not generate Markdown output or migration recommendations.
- A detected algorithm name is not a security assessment. Review the matching source and applicable TSAR cryptography rules.
