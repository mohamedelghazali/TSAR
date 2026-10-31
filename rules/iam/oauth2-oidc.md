# OAuth 2.1 and OIDC

## Flow Selection
- Authorization Code with PKCE for public clients (SPA, mobile).
- Authorization Code with client authentication for confidential clients.
- Client Credentials for machine-to-machine.
- Device Authorization for constrained devices.
- Forbidden: Implicit flow, Resource Owner Password Credentials.

## Tokens
- Access tokens: JWT, short-lived (<= 15 minutes), audience-bound.
- Refresh tokens: opaque, rotated on each use, bound to client, revocable.
- ID tokens: for authentication only, not authorization.
- Never accept tokens without signature verification and claim validation.

## Claim Validation
- `iss` matches expected issuer exactly.
- `aud` matches expected audience.
- `exp`, `iat`, `nbf` within clock skew.
- `alg` matches allowed algorithm; reject `none`.
- Key ID (`kid`) maps to a known key; refresh JWKS on rotation.

## Scopes
- Minimal scopes per operation.
- Never request `*` or overly broad scopes.
- Resource server enforces scope + object-level authorization.

## PKCE
- `S256` code challenge method only; `plain` forbidden.
- `state` parameter validated on callback.
- `nonce` for OIDC ID tokens.

## Redirect URIs
- Exact match; no wildcards.
- `https` only (except `localhost` for development).
- No open redirectors.

## Forbidden
- Tokens in URL fragments for server-side apps.
- Access tokens used as session identifiers.
- Long-lived refresh tokens without rotation.
