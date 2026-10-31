# Identity Federation Guide

## SAML vs OIDC
| Aspect | SAML 2.0 | OIDC |
|---|---|---|
| Format | XML | JSON/JWT |
| Mobile/SPA | Poor | Good |
| Enterprise SSO | Mature | Growing |
| Standard | OASIS | OpenID Foundation |

Prefer OIDC for new deployments. Use SAML only when required by an IdP or SP.

## Federation Checklist
- [ ] IdP signs with RSA-SHA256 or better.
- [ ] SP validates signature on assertion and response.
- [ ] InResponseTo and nonce validated.
- [ ] Assertion replay prevented.
- [ ] Session lifetime bounded.
- [ ] Logout propagated.
- [ ] Metadata refreshed from signed source.
- [ ] Admin MFA enforced.

## Provisioning
- SCIM 2.0 for user lifecycle.
- Deprovisioning propagates within 5 minutes.
- No shared tokens across tenants.
- Audit every provisioning event.
