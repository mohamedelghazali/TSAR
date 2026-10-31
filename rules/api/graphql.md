# GraphQL Security

## Query Cost
- Query depth limit (<= 10).
- Query complexity limit; reject queries exceeding a cost threshold.
- Pagination required; no unbounded lists.
- Rate limits per user and per operation type.

## Authorization
- Field-level authorization enforced in resolvers.
- No reliance on client-provided claims without server verification.
- Introspection disabled in production (unless explicitly public).

## Input Validation
- Schema-driven validation for every argument.
- Reject unknown fields; strict mode.
- Sanitize before any sink (SQL, shell, template).

## Batching and Aliases
- Limit aliases per query.
- Limit batched mutations; mutations are not batched by default.
- Detect and block malicious patterns (deep aliasing, fragment cycles).

## Error Handling
- Generic error messages; log details server-side.
- Never expose stack traces, SQL errors, or internal paths.

## Persisted Queries
- Allow-list of approved persisted queries in production.
- Reject arbitrary queries unless explicitly needed.

## Forbidden
- Introspection in production (without auth).
- Unbounded recursion in resolvers.
- Exposing `__schema` to unauthenticated users.
