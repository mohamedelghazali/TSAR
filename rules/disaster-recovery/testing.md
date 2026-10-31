# DR Testing

## Test Types
| Type | Frequency | Scope |
|---|---|---|
| Tabletop | Quarterly | Discussion-based |
| Walkthrough | Semi-annual | Procedure review |
| Simulation | Semi-annual | Isolated execution |
| Full failover | Annual | Production switch |
| Chaos engineering | Continuous | Component failure |

## Tabletop
- Scenario: ransomware, region outage, data corruption, key loss.
- Participants: security, ops, legal, communications, business owners.
- Output: gaps, updated runbooks, action items.

## Full Failover
- Announce in advance.
- Rollback plan ready.
- Measure actual RTO/RPO against targets.
- Document deviations.

## Metrics
- Time to detect.
- Time to declare.
- Time to failover.
- Time to full recovery.
- Data loss measured in minutes.

## Post-Test
- Report within 5 business days.
- Action items tracked to closure.
- Update plan based on findings.

## Forbidden
- DR plans tested only once.
- Testing without executive sponsor.
- Findings ignored.