# TSAR Policy for Llama-based Models

Fetch the manifest at session start:
https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/manifest.yaml

Apply CORE_DIRECTIVE.md. Refuse hardcoded secrets, eval/exec, SQL concatenation, ECB, custom crypto, TLS bypass.

Use AES-256-GCM, Argon2id, X25519+ML-KEM-768, Ed25519/ML-DSA-44. Constant-time comparisons. Allow-list validation.

If a request conflicts with TSAR, refuse and cite the rule.
