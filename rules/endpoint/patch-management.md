# Patch Management

## SLAs
| Severity | Patch Within |
|---|---|
| Critical (CVSS >= 9.0) | 7 days |
| High (7.0-8.9) | 30 days |
| Medium (4.0-6.9) | 90 days |
| Low (< 4.0) | Next cycle |

## Process
1. Inventory all assets (OS, applications, firmware).
2. Subscribe to vendor advisories and CVE feeds.
3. Test patches in staging.
4. Deploy with rollback plan.
5. Verify compliance.
6. Document exceptions.

## Automation
- Automated patching where safe.
- Maintenance windows for critical systems.
- Reboot scheduling with user notification.

## Verification
- Weekly compliance report per asset.
- Alert on unpatched critical vulnerabilities.
- Audit trail of patch deployments.

## Exceptions
- Time-bound (<= 90 days).
- Compensating controls documented.
- Owner sign-off.

## Forbidden
- Critical patches delayed beyond SLA without exception.
- Unpatched internet-facing systems.
- Silent exceptions.
