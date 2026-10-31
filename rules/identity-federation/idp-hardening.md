# Identity Provider Hardening

## Administrative Access
- MFA enforced for all admin accounts; FIDO2 preferred.
- Just-in-time elevation via PIM/PAM.
- No standing global admin.
- Admin actions logged and reviewed weekly.

## Signing Keys
- IdP signing keys rotated annually; emergency rotation documented.
- Keys stored in HSM.
- Old keys retained for token validation window only.

## Session
- Session lifetime <= 12 hours.
- Idle timeout <= 30 minutes for admin.
- Continuous access evaluation (CAE) where supported.

## Policies
- Conditional Access enforced for risky sign-ins.
- Block legacy authentication protocols.
- Named locations and device compliance for sensitive apps.

## Audit
- All authentication events streamed to SIEM.
- Failed authentication alerting with thresholds.
- Anomaly detection on sign-in patterns.

## Forbidden
- Password-only authentication for admins.
- Shared admin accounts.
- Disabled MFA "temporarily".
- Long-lived API tokens for admin automation.
