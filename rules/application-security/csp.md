# Content Security Policy (Advanced)

## Baseline Policy
```
default-src 'none';
script-src 'nonce-{random}' 'strict-dynamic' 'unsafe-inline' 'unsafe-eval';
style-src 'nonce-{random}' 'unsafe-inline';
img-src 'self' data: https://cdn.example.com;
font-src 'self' https://fonts.example.com;
connect-src 'self' https://api.example.com;
frame-ancestors 'none';
form-action 'self';
base-uri 'none';
object-src 'none';
upgrade-insecure-requests;
require-trusted-types-for 'script';
trusted-types default;
report-to csp-endpoint;
```

## Rationale
- `unsafe-inline` and `unsafe-eval` are ignored by modern browsers when a nonce is present, but provide compatibility with old browsers.
- `strict-dynamic` allows nonce-loaded scripts to load further scripts without nonce.
- `default-src 'none'` blocks anything not explicitly allowed.

## Reporting
- `Report-To` header with `csp-endpoint` group.
- `Reporting-Endpoints` for modern browsers.
- Endpoint authenticates reports and stores them with retention.
- Alert on high-volume reports (misconfiguration or attack).

## Rollout
1. Deploy in `Content-Security-Policy-Report-Only` for 2 weeks.
2. Review reports daily.
3. Fix violations.
4. Switch to enforcing.
5. Keep report-only for legacy paths.

## Forbidden
- `default-src *`.
- `script-src 'unsafe-inline'` without nonce.
- `script-src 'unsafe-eval'` in production.
- Missing `frame-ancestors` on pages that must not be framed.
```
