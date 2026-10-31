# Messaging Integration Guide

## Choosing a Broker
| Broker | When | Rules |
|---|---|---|
| Kafka | High throughput, event streaming | rules/messaging/kafka.md |
| RabbitMQ | Complex routing, task queues | rules/messaging/rabbitmq.md |
| NATS | Low latency, IoT, edge | rules/messaging/nats.md |
| Cloud Pub/Sub | Managed, multi-cloud | rules/messaging/pubsub.md |

## Common Requirements
- TLS 1.3 for all broker connections.
- Per-application credentials (mTLS or SCRAM).
- Least-privilege ACLs per topic.
- Idempotent consumers (rules/messaging/idempotency.md).
- Dead-letter queues with bounded retention.
- Message-level encryption for PII.

## Deployment Checklist
- [ ] TLS enforced, plaintext listeners disabled.
- [ ] Auth configured, default users disabled.
- [ ] ACLs reviewed, no wildcards.
- [ ] Schema registry authenticated.
- [ ] DLQ configured and monitored.
- [ ] Idempotency keys implemented.
- [ ] Backups encrypted.
