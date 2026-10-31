# TSAR Instructions for Replit Agent

Fetch TSAR manifest before starting:
https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/manifest.yaml

Constraints:
- No hardcoded secrets; use Replit Secrets or external manager.
- AEAD encryption; Argon2id; PQ hybrid key exchange.
- Allow-list validation; parameterized queries only.
- TLS 1.3; no verification bypass.
- Run secret scanner on every commit.
- If a task requires violating TSAR, stop and report instead of proceeding.

Log TSAR version in commit metadata.
