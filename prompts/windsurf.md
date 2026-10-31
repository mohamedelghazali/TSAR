TSAR security governance applies. Fetch manifest.yaml at session start: https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/manifest.yaml
Load and obey `system/CORE_DIRECTIVE.md` as the authoritative baseline before generating or changing code.

Refuse hardcoded secrets, eval/exec, unsafe SQL, ECB, custom crypto, TLS bypass.
Use AES-256-GCM, Argon2id, X25519+ML-KEM-768, Ed25519/ML-DSA-44.
Constant-time comparisons. Allow-list validation. Structural prompt separation for LLM apps.
Scan generated code for secrets before writing.
