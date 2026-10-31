# SCIM Provisioning

## Transport
- HTTPS only; mTLS optional but recommended.
- Bearer token authentication; rotate tokens per policy.

## Schema
- Strict schema validation; reject unknown attributes.
- `externalId` required for stable mapping.

## Provisioning
- Deprovisioning must revoke access immediately (not just disable).
- Group changes propagate to authorization systems within 5 minutes.
- Log every create/update/delete with actor identity.

## Failures
- Retry with exponential backoff.
- Alert on repeated failures; do not silently drop.

## Forbidden
- Plaintext SCIM endpoints.
- Tokens shared across tenants.
- Bulk deprovision without a grace period and notification.
