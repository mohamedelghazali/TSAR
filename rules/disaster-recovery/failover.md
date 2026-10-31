# Failover Procedures

## Pre-Conditions
- Replicated data verified in sync.
- DNS TTL lowered to 60 seconds.
- Standby infrastructure provisioned and healthy.
- Credentials available (break-glass).
- Communications sent to stakeholders.

## Execution
1. Declare disaster (authority documented).
2. Freeze writes to primary (or fence it).
3. Verify standby health.
4. Promote standby (database, message broker).
5. Update DNS / traffic routing.
6. Verify application health.
7. Notify stakeholders.
8. Monitor for issues.

## Failback
- Only after primary is healthy and verified.
- Reverse the process.
- Test in staging first.
- Schedule in low-traffic window.

## Credentials
- Break-glass credentials in sealed envelope or vault with two-person approval.
- Access logged and reviewed after use.
- Rotated after each use.

## Forbidden
- Failover without fencing primary (split-brain).
- Failover without verification.
- Permanent reliance on break-glass credentials.