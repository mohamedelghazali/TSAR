# Database Replication Security

## Transport
- TLS 1.3 between primary and replicas.
- Mutual authentication (client certificates).
- No plaintext replication.

## Identity
- Dedicated replication user with minimal privileges.
- Distinct credentials per replica.
- Rotate replication credentials annually.

## Integrity
- Verify checksums on replicas.
- Detect divergence via periodic consistency checks.
- Alert on replication lag exceeding threshold.

## Failover
- Automatic failover with quorum.
- Split-brain prevention (STONITH or quorum-based).
- Failover events logged and alerted.

## Backups from Replicas
- Replicas can serve backups; still encrypt at rest.
- Verify backup integrity from replica matches primary at snapshot time.

## Forbidden
- Plaintext replication streams.
- Shared replication credentials across replicas.
- Replicas exposed publicly.
