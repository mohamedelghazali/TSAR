# Application Security Guide

## Platforms
| Platform | Key Rules |
|---|---|
| SPA | rules/application-security/spa.md |
| Mobile | rules/application-security/mobile-app.md |
| Desktop | rules/application-security/desktop-app.md |

## Cross-Platform Requirements
- Tokens never in `localStorage` for high-value apps.
- CSP with nonce; no `unsafe-inline`.
- Certificate pinning for mobile and desktop.
- Signed updates for desktop.
- Root/jailbreak/tamper detection for Tier-1.

## Verification
- [ ] CSP enforced; reports reviewed.
- [ ] SRI on all third-party assets.
- [ ] No secrets in client bundles.
- [ ] Session tokens in HttpOnly cookies or in-memory only.
- [ ] Deep links validated.
- [ ] Code obfuscated where required.
