# TSAR Dashboard

The `tools/tsar-web` dashboard provides a read-only view of TSAR coverage.

## Features
- Manifest version and last update.
- Active file count per domain.
- Missing file detection.
- Static export support.

## Security
- No external requests.
- Strict CSP.
- No telemetry.
- Intended for internal use behind SSO.

## Deployment
1. `cd tools/tsar-web`
2. `npm install && npm run build`
3. Serve behind an authenticated reverse proxy.
4. Restrict access to security team.

## Limitations
- Does not display scanner findings (use SARIF).
- Does not modify rules.
- Requires manual refresh after manifest updates.
