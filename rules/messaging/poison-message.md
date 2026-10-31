# Poison Message Handling

## Detection
- Retry count per message tracked.
- Alert when a message exceeds `max_attempts` (default 5).
- Log with message_id and failure reason (never payload contents for PII).

## Handling
- Route to dead-letter queue after max attempts.
- DLQ access requires elevated authorization.
- DLQ has bounded retention; triage within SLA.

## Recovery
- Manual inspection of DLQ by authorized operator.
- Fix and replay via a controlled pipeline.
- Never replay blindly; validate fix first.

## Monitoring
- Alarm on DLQ depth growth.
- Alarm on message age in queue.
- Track poison message rate per topic.

## Forbidden
- Infinite retries.
- Discarding poison messages without DLQ.
- DLQ readable by production application credentials.
