# A01: Broken Access Control

## Principle
Every request is authorized server-side. Client-side checks are UX only.

## Controls
- Deny by default; explicit grants per role and resource.
- Enforce on every endpoint, including internal and admin APIs.
- Object-level authorization: verify the authenticated user owns the requested resource ID.
- No IDOR: never trust client-supplied user IDs, tenant IDs, or role claims without server verification.
- Centralize authorization logic in a single policy layer.
- Log authorization failures with user ID, resource, and timestamp.

## Forbidden
- Relying on hidden UI elements or client-side route guards.
- Trusting JWT claims without signature verification.
- Wildcard permissions on production roles.
