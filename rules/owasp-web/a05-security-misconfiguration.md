# A05: Security Misconfiguration

## Controls
- No default credentials shipped; forced rotation on first boot.
- Debug mode disabled in production; verbose errors suppressed.
- Directory listing disabled.
- Unused features, ports, and services removed.
- Security headers enforced (see rules/platform/web.md).
- Container images: non-root user, read-only filesystem, minimal base.

## Forbidden
- Stack traces or internal paths in HTTP responses.
- Default admin endpoints exposed to the internet.
- CORS wildcard on authenticated endpoints.
