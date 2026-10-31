# A10: Server-Side Request Forgery (SSRF)

## Controls
- Allow-list of outbound destinations per service.
- DNS rebinding protection: resolve, validate IP, then connect using the resolved IP.
- Block private IP ranges, loopback, link-local, and metadata endpoints (169.254.169.254).
- Disable unnecessary URL schemes (file://, gopher://, dict://).
- Response size limits and timeouts on outbound requests.
- Authentication removed from outbound requests unless explicitly required.

## Forbidden
- Fetching user-supplied URLs without validation.
- Following redirects to internal hosts.
