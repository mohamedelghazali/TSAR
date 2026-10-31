# Web Security Baseline

## Headers (Mandatory)
- `Content-Security-Policy` with nonce-based script-src, no `unsafe-inline`.
- `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`.
- `X-Content-Type-Options: nosniff`.
- `Referrer-Policy: strict-origin-when-cross-origin`.
- `Permissions-Policy` restricting camera, microphone, geolocation.

## Cookies
- `HttpOnly`, `Secure`, `SameSite=Strict` (or `Lax` with CSRF token).
- `__Host-` prefix for critical cookies.

## Input & Output
- Allow-list validation server-side.
- Output encoding context-aware (HTML, JS, URL, CSS).
- Trusted Types API where supported.
- Subresource Integrity (SRI) for third-party scripts.

## Sessions & Auth
- Rotate session ID on login.
- Short-lived access tokens + rotating refresh tokens.
- CSRF tokens for state-changing requests.
