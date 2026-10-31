# Alerting Security

## Signal Quality
- Alerts actionable; every alert has a runbook.
- Severity mapped to response time.
- No alert fatigue: deduplicate, group, and route.

## Sensitive Alerts
- Auth failures spike, privilege escalation, data exfiltration patterns.
- Alert channels authenticated; no open webhooks.
- Alert content: no secrets, no PII.

## Delivery
- Redundant channels (email, chat, pager).
- Acknowledge and escalate on no-response.
- Alert storms suppressed with grouping.

## False Positives
- Tune alerts weekly.
- Track false positive rate; retire alerts with high noise.

## Forbidden
- Alerts containing raw logs with PII.
- Unauthenticated webhook endpoints.
- Alerts without runbooks.
