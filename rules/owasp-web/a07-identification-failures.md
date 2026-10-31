# A07: Identification and Authentication Failures

## Controls
- Password policy: minimum 12 characters, no composition rules, breach-list check.
- Argon2id with parameters in rules/crypto/algorithms.md.
- MFA required for admin and Tier-1 accounts.
- Session rotation on login and privilege change.
- Account lockout with exponential backoff, not permanent lock.
- Credential recovery via out-of-band channel with single-use token.
- Constant-time comparison for all tokens.

## Forbidden
- Security questions as sole recovery factor.
- Session IDs in URLs.
- Persistent sessions without rotation.
- Comparing tokens with `==`.
