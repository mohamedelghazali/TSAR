# Cloud Pub/Sub Security (GCP, AWS SNS/SQS, Azure Service Bus)

## Transport
- TLS enforced by provider; verify endpoint TLS version >= 1.2.
- For Azure Service Bus: `RequireTls` mandatory.

## Authentication
- Workload identity (Workload Identity, IRSA, Managed Identity).
- No long-lived service account keys.
- Per-topic/queue permissions.

## Encryption
- Customer-managed keys (CMEK/CMK) for sensitive topics.
- Message-level encryption for PII payloads.
- Encrypted dead-letter queues.

## Access Control
- IAM policies scoped per resource.
- No `pubsub.topics.publish` on `*` in production.
- Subscription-level access for consumers.

## Delivery
- Idempotency keys; consumers deduplicate.
- Retry with exponential backoff and DLQ.
- Message TTL bounded.

## Forbidden
- Public topics/queues.
- Publisher/subscriber roles at project level.
- PII without message-level encryption.
