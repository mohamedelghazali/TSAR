# Apache Kafka Security

## Transport
- TLS 1.3 only for broker and client listeners.
- Disable plaintext listeners in production.
- `ssl.endpoint.identification.algorithm=https` mandatory.

## Authentication
- SASL/SCRAM-SHA-512 or mTLS with short-lived certs.
- No PLAINTEXT or SASL/PLAIN in production.
- Per-application principal; no shared credentials.

## Authorization
- Kafka ACLs enabled (`authorizer.class.name`).
- Principle of least privilege: per-topic read/write, per-group consume.
- Deny by default; explicit grants only.
- Audit ACL changes; alert on new grants.

## Encryption at Rest
- Broker disks encrypted (LUKS or cloud equivalent).
- Message-level encryption for sensitive payloads (AES-256-GCM, envelope encryption).

## Topics
- Naming convention: `<domain>.<entity>.<event>.v<n>`.
- Retention per classification; PII topics shortened.
- `min.insync.replicas >= 2` with `acks=all` for durability.

## Schema Registry
- Schema validation enforced; no raw untyped payloads.
- Registry authenticated; access controlled.
- Schema evolution compatible (backward/forward per policy).

## Forbidden
- PLAINTEXT listeners.
- Wildcard ACLs (`*` principal, `*` topic) in production.
- Publishing PII without message-level encryption.
- Auto topic creation in production.
