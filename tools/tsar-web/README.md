# TSAR Web Dashboard

Read-only dashboard that inspects the TSAR manifest and reports coverage.

## Usage
```bash
cd tools/tsar-web
npm install
npm run dev
```

Open `http://localhost:3000`.

## Security
- Read-only; no write operations.
- No external network requests.
- CSP restricts to self.
- No analytics, no telemetry.

## Deployment
Static export is supported:
```bash
npm run build
# Deploy the `.next/static` output behind your SSO-protected proxy.
```

Do not deploy without authentication in front. The dashboard is intended for
security teams only.
