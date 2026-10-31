# Idempotency for Message Handlers

## Requirement
Every consumer must be idempotent for at-least-once delivery.

## Implementation
- Producer attaches a unique `message_id` (UUIDv4 or ULID).
- Consumer stores `message_id` in a deduplication table with TTL >= max retry window.
- Processing: check -> process -> commit -> mark processed (transactional where possible).
- Duplicates return the same result; no side effects repeated.

## Side Effects
- External calls require idempotency keys (payment APIs, HTTP with `Idempotency-Key`).
- Database writes use upserts or versioned rows.
- Notifications: dedupe before send.

## Failure Modes
- Crash after process, before commit: reprocess (idempotent).
- Crash after commit, before mark: reprocess returns same result via dedupe.

## Forbidden
- Processing without a dedupe key.
- Relying on broker-level deduplication alone.
- At-most-once delivery for critical flows.
