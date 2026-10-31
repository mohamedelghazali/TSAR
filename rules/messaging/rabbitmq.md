# RabbitMQ Security

## Transport
- TLS 1.3 for AMQP and management API.
- Disable plaintext AMQP listener.
- Verify peer certificates; no `verify_none`.

## Authentication
- Per-application users with unique passwords or mTLS.
- No `guest` user in production; disable it.
- Rotate credentials per policy.

## Authorization
- Vhost isolation per environment and tenant.
- Permissions: configure, write, read scoped to specific resources.
- No `.*` patterns across vhosts.

## Queues and Exchanges
- Durable queues with `x-queue-type: quorum` for high availability.
- Dead-letter exchanges configured; alerts on DLQ depth.
- Message TTL enforced to prevent unbounded growth.

## Management API
- Bind to localhost or private network only.
- TLS with certificate verification.
- Rate limits and audit logs enabled.

## Forbidden
- `guest`/`guest` accessible from non-localhost.
- AMQP over plaintext.
- Global permissions with `.*` across all vhosts.
- Unbounded queues without TTL.
