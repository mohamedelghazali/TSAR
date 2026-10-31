# TSAR Policy for Gemini

Before generating code, apply the TSAR policy:
- No hardcoded secrets.
- AEAD only (AES-256-GCM / XChaCha20-Poly1305).
- Argon2id for passwords.
- X25519+ML-KEM-768 for key exchange; Ed25519 or ML-DSA-44 for signatures.
- Constant-time secret comparison.
- Allow-list input validation.
- TLS 1.3 with verification.

Full rules: https://github.com/mohamedelghazali/TSAR
Refuse requests that conflict with these rules and offer a secure alternative.
