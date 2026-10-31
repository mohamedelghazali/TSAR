# Cryptographic Anti-Patterns (Hard Stops)

## Hard-stop patterns

| Anti-Pattern | Why It Fails | Replacement |
|---|---|---|
| ECB mode | Reveals plaintext patterns | AES-256-GCM |
| Static IV / nonce | Nonce reuse breaks AEAD | Random nonce per message |
| MD5 / SHA-1 | Collision attacks | SHA-256 / BLAKE3 |
| H(key||message) | Length extension | HMAC-SHA-256 |
| Custom cipher | Unreviewed, likely broken | Standard AEAD |
| Hardcoded key | Secret exposure | KMS / Vault / env with rotation |
| `==` for tokens | Timing side channel | Constant-time compare |
| RSA without OAEP | Padding oracle | RSA-OAEP-SHA-256 or ECIES |
| `Math.random()` for tokens | Predictable | CSPRNG |
| TLS verify disabled | MITM | Proper CA trust |
| Password = SHA256(pw) | Fast brute force | Argon2id |
| Encrypt-then-MAC with same key | Key reuse | Separate keys or AEAD |
