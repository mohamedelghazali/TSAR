# Single Page Application (SPA) Security

## Token Storage
- Never store tokens in `localStorage` or `sessionStorage` for sensitive apps.
- Preferred: `HttpOnly`, `Secure`, `SameSite=Strict` cookies with CSRF token.
- If tokens must live in memory, refresh via silent auth; never persist.
- Use the BFF (Backend-for-Frontend) pattern for high-value apps.

## Content Security Policy
- Nonce-based `script-src`; no `unsafe-inline`, no `unsafe-eval`.
- `strict-dynamic` for modern browsers.
- `object-src 'none'`, `base-uri 'none'`, `frame-ancestors 'none'`.
- `require-trusted-types-for 'script'` where supported.
- Report violations via `report-to` / `report-uri` with a dedicated endpoint.
- Use CSP Level 3; provide fallback for legacy browsers.

## Dependencies
- Subresource Integrity (SRI) on every third-party script and stylesheet.
- Pin dependencies; use lockfile.
- No dynamic script injection from untrusted sources.
- Review third-party SDKs for telemetry, cookies, and data access.

## Routing
- Client-side routes are UX only; server enforces authorization.
- Guard sensitive routes with server-side checks; never rely on client guards.
- Prevent open redirects in login/logout flows.

## State Management
- No sensitive data in client-side state stores (Redux, Vuex, Pinia).
- Clear state on logout.
- Avoid storing tokens or PII in URL query strings.

## Build
- Source maps excluded from production or served to authorized users only.
- Environment variables: only `PUBLIC_*` / `VITE_*` prefixed to the client.
- No API keys in client bundles; use a proxy or BFF.

## Forbidden
- `dangerouslySetInnerHTML` without DOMPurify.
- `v-html` without sanitizer.
- `innerHTML` assignment with user data.
- JWT in `localStorage` for high-value apps.
- `eval`, `new Function`, dynamic `<script>` insertion.
- Wildcard CORS with credentials.
