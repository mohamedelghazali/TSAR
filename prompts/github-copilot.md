# TSAR Security Instructions for GitHub Copilot

This repository is governed by TSAR. Fetch and apply the current `manifest.yaml` and `system/CORE_DIRECTIVE.md` before suggesting code:
- Do not generate hardcoded secrets, eval/exec, unsafe SQL, ECB mode, or custom crypto.
- Use AES-256-GCM, Argon2id, X25519+ML-KEM-768, Ed25519/ML-DSA-44.
- Validate all user input with allow-lists.
- Use constant-time comparison for secrets.
- Enforce TLS 1.3 and certificate verification.

Fetch full rules: https://github.com/mohamedelghazali/TSAR
