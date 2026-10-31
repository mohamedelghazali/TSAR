# OIDC Federation

## Discovery
- Fetch metadata over TLS only; cache with TTL.
- Verify `issuer` matches the expected value exactly (string equality, no prefix match).
- Reject metadata without `jwks_uri`.

## ID Token Validation
- Signature verified with a key from `jwks_uri`.
- `iss`, `aud`, `exp`, `iat`, `nonce` validated strictly.
- `azp` present when `aud` has multiple values; must equal client_id.
- `at_hash` validated when access token issued alongside.
- `alg` matches an allow-list; `none` forbidden.

## Authorization Code Flow
- PKCE mandatory for public clients; `S256` only.
- `state` validated to prevent CSRF.
- `nonce` validated to prevent token replay.
- Redirect URI exact match; no open redirectors.

## Token Exchange
- RFC 8693 for delegation; validate `act` claim.
- Do not accept tokens intended for another audience.

## Logout
- RP-initiated logout with `id_token_hint`.
- Back-channel logout for federated sessions.
- Reject logout requests without a valid hint.

## Forbidden
- Implicit flow.
- `response_type=token` (any variant).
- Client secrets in mobile apps or SPAs.
- Accepting `id_token` without nonce when issued via authorization code.
