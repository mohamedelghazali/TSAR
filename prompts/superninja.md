# TSAR Instructions for SuperNinja

Fetch the TSAR `manifest.yaml` and load `system/CORE_DIRECTIVE.md` before any task:
https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/manifest.yaml

Constraints:
- No hardcoded secrets; use platform secret manager.
- AEAD encryption; Argon2id; PQ hybrid key exchange.
- Allow-list validation; parameterized queries only.
- TLS 1.3; no verification bypass.
- Scope tools to minimum; require human confirmation for irreversible actions.
- Run secret scanner on every commit.

Log TSAR version in commit metadata.
