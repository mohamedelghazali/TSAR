# LLM10: Unbounded Consumption

## Risk
Unlimited resource consumption (tokens, API calls, compute) can lead to cost
overruns, denial of service, or resource exhaustion affecting other users.

## Controls
- Token budget per request and per user per period.
- Rate limits per identity and per endpoint.
- Timeout on every model call.
- Maximum output token limit enforced.
- Cost anomaly detection with alerts.
- Kill switch for runaway consumption.
- Tenant quotas for multi-tenant deployments.

## Limits Matrix
| Dimension | Default Limit |
|---|---|
| Input tokens per request | 32k |
| Output tokens per request | 4k |
| Requests per user per minute | 60 |
| Requests per tenant per day | 100k |
| Session duration | 30 min idle |
| Concurrent sessions per user | 3 |

## Monitoring
- Cost per user, per tenant, per model.
- Anomaly alerts on cost spikes.
- Rate limit hits tracked.
- Denied requests logged (potential probing).

## Response
- Throttle at limit; return explicit error.
- Notify tenant admin on quota approach.
- Kill switch for compromised accounts.
- Investigate patterns of abuse.

## Forbidden
- Unbounded output length.
- No rate limits in production.
- Shared API keys across tenants without quotas.
- Ignoring cost anomalies.
