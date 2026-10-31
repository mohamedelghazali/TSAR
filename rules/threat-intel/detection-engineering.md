# Detection Engineering

## Detection Types
| Type | Use | False Positive Rate |
|---|---|---|
| Signature | Known bad | Low |
| Anomaly | Behavioral deviation | Medium |
| Heuristic | Pattern-based | Medium |
| Threat hunting | Hypothesis-driven | N/A |

## Rule Quality
- Every detection has: description, severity, false positive rate, runbook.
- MITRE ATT&CK technique mapped.
- Tested with positive and negative test cases.
- Reviewed quarterly for effectiveness.

## Tuning
- Baseline normal behavior.
- Reduce noise: aggregation, thresholds, context.
- Document suppressions with expiry.

## Metrics
- Precision, recall per rule.
- Mean time to detect (MTTD).
- Alert-to-ticket ratio.

## Forbidden
- Detections without runbooks.
- Untuned rules generating > 10 false positives/week.
- Suppressions without expiry.
