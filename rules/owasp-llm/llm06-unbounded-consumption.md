# LLM06: Unbounded Consumption

## Risk
Unbounded token use, model calls, tool loops, context growth, or compute can cause denial of service, runaway costs, and resource exhaustion across tenants.

## Controls
- Enforce input and output token budgets per request, user, tenant, and model.
- Apply rate limits and concurrency limits at identity and tenant boundaries.
- Set hard timeouts and maximum tool-call/agent-loop iterations.
- Bound retrieval result counts, context size, file sizes, and generated output.
- Apply cost budgets, anomaly alerts, circuit breakers, and emergency kill switches.
- Use fair scheduling and isolate tenant quotas.
- Require explicit approval before raising production quotas.

## Limits Matrix
| Dimension | Required Control |
|---|---|
| Input/output tokens | Model-specific hard limits |
| Requests | Per-user and per-tenant rate limits |
| Tool calls | Maximum calls and recursion depth |
| Runtime | Deadline and cancellation propagation |
| Cost | Budget, alerts, and circuit breaker |
| Concurrency | Tenant-aware quotas |

## Testing
- Test prompt-driven loops and recursive tool invocation.
- Verify timeouts cancel downstream work.
- Simulate quota exhaustion and cost spikes.
- Confirm one tenant cannot consume another tenant's reserved capacity.

## Forbidden
- Unlimited agent loops or tool invocations.
- Production model endpoints without quotas and timeouts.
- Silent quota increases or shared unmetered tenant budgets.
