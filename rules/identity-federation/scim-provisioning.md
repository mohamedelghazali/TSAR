# SCIM 2.0 Provisioning at Scale

## Authentication
- OAuth 2.0 bearer token from the IdP, rotated per policy.
- mTLS optional but recommended for cross-tenant provisioning.
- Token scoped to a single tenant; no shared tokens.

## Endpoints
- `/Users`, `/Groups` implemented per RFC 7644.
- Filtering supported (`filter=userName eq "..." `); no full scans.
- Bulk operations: rate-limited, idempotent, validated per item.

## Idempotency
- Provisioning operations idempotent by `externalId`.
- Duplicate creates return `409 Conflict` with the existing ID.

## Deprovisioning
- Deactivation (`active=false`) triggers immediate access revocation.
- Soft delete kept for 30 days; hard delete after retention.
- Deprovisioning events audited.

## Error Handling
- Partial bulk results per item.
- Retry with exponential backoff; DLQ for failures.

## Forbidden
- Shared tokens across tenants.
- Silent deprovisioning without audit.
- Bulk deprovision without grace period and notification.
