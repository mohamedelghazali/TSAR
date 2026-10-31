# NATS Security

## Transport
- TLS 1.3 for client and cluster connections.
- Verify peer certificates.
- `no_tls` forbidden in production.

## Authentication
- NATS 2.0 with JWT-based accounts and NKeys.
- Per-application identities; no shared credentials.
- Decentralized authentication via operator JWT.

## Authorization
- Per-subject publish/subscribe permissions.
- No `>` (all subjects) grants except for audited infrastructure.
- Deny by default.

## JetStream
- Encryption at rest for streams (XChaCha20-Poly1305 or AES-256-GCM).
- Retention policies per stream.
- Consumer acknowledgment required; no auto-ack in production.

## Leafnodes and Gateways
- TLS-only between clusters.
- Explicit allow-lists for leafnode connections.

## Forbidden
- `authorization { users = [{user: "test", password: "test"}] }` in production.
- Wildcard permissions on `>` for client accounts.
- Unencrypted JetStream data on disk.
