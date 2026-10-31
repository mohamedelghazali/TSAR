# Disaster Recovery Planning

## Objectives
| Tier | RTO | RPO |
|---|---|---|
| Tier 1 (critical) | 1 hour | 5 minutes |
| Tier 2 (important) | 4 hours | 1 hour |
| Tier 3 (standard) | 24 hours | 24 hours |
| Tier 4 (low) | 72 hours | 72 hours |

## Components
1. Business impact analysis (BIA).
2. Risk assessment per system.
3. Recovery strategy per tier.
4. Communication plan.
5. Roles and responsibilities.
6. Testing schedule.

## Recovery Strategies
| Strategy | RTO | Cost |
|---|---|---|
| Backup/restore | Hours to days | Low |
| Pilot light | Minutes to hours | Medium |
| Warm standby | Seconds to minutes | High |
| Multi-site active/active | Zero | Highest |

## Documentation
- Runbooks per system.
- Contact lists updated quarterly.
- Vendor escalation paths.
- Regulatory notification requirements.

## Forbidden
- DR plan without tested runbooks.
- RTO/RPO without business sign-off.
- Untested communication plans.