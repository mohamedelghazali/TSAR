# REST API Security

## Authentication
- OAuth 2.1 / OIDC for user-facing APIs.
- mTLS or short-lived tokens for service-to-service.
- No API keys in query strings; use Authorization header only.

## Authorization
- Object-level authorization on every endpoint.
- Deny by default; explicit grants.
- Centralize policy; no scattered `if user.role == ...` checks.

## Input Validation
- Schema validation on every request body, query parameter, and header.
- Reject unknown fields (strict schema).
- Limit payload size, header count, URL length, JSON depth.

## Output
- No stack traces, internal errors, or version banners.
- Return consistent error format; never leak which field failed auth.
- Rate-limit error responses to prevent enumeration.

## Headers
- `Content-Type` strictly enforced.
- `Cache-Control: no-store` on authenticated responses.
- CORS: explicit origins; no wildcard on authenticated endpoints.

## Versioning
- `/v1/` explicit; deprecation policy documented.
- Breaking changes require a new version.

## Forbidden
- API keys in URLs.
- Idempotency keys optional for unsafe methods; required for payments.
- Returning internal IDs to untrusted clients.
