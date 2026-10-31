# Data Subject Requests (DSR)

## Rights
| Right | Response Time |
|---|---|
| Access (Art. 15) | 30 days |
| Rectification (Art. 16) | 30 days |
| Erasure (Art. 17) | 30 days |
| Restriction (Art. 18) | 30 days |
| Portability (Art. 20) | 30 days |
| Object (Art. 21) | Immediate for direct marketing |

## Process
1. Verify identity (proportional to data sensitivity).
2. Locate all data across systems (inventory).
3. Fulfill request in machine-readable format where applicable.
4. Propagate erasure to backups, derived data, third parties.
5. Document the request and fulfillment.

## Tooling
- DSR portal for users.
- Automated data discovery across databases, logs, backups.
- Integration with processing systems for erasure.

## Verification
- Test DSR flow quarterly with synthetic data.
- Measure fulfillment time; alert if approaching SLA.
- Audit a sample of DSRs monthly.

## Forbidden
- Charging for DSR fulfillment (except manifestly unfounded).
- Refusing without legal basis.
- Fulfilling without identity verification.
- Partial erasure leaving derived data.
