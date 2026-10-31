# Disaster Recovery Guide

## Tiers
| Tier | RTO | RPO | Example |
|---|---|---|---|
| 1 | 1h | 5min | Payments, auth |
| 2 | 4h | 1h | Customer portal |
| 3 | 24h | 24h | Internal tools |
| 4 | 72h | 72h | Analytics |

## Planning
1. Business impact analysis.
2. Identify tier per system.
3. Define recovery strategy per tier.
4. Document runbooks.
5. Assign roles.
6. Schedule tests.

## Testing Cadence
- Tabletop: quarterly.
- Simulation: semi-annual.
- Full failover: annual.

## Post-Test
- Report within 5 business days.
- Track action items to closure.
- Update plan.