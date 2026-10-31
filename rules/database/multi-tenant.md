# Multi-Tenant Database Design

## Isolation Levels
| Model | Use | Risk |
|---|---|---|
| Database per tenant | High isolation, high cost | None (if enforced) |
| Schema per tenant | Medium isolation, medium cost | Search-path injection |
| Row-level (RLS) | Low cost, requires rigor | Missing predicate leaks data |

## Row-Level Security
- RLS enforced at the database engine (Postgres RLS, Oracle VPD, SQL Server RLS).
- Application cannot bypass RLS; no `BYPASSRLS` for app users.
- Tenant ID set per session via a parameter bound to the authenticated user.
- Every query includes tenant context; test with fuzzing.

## Application-Level
- Never rely on application filtering alone.
- Enforce tenant ID at the data-access layer; reject queries without tenant context.
- Cache keys include tenant ID.

## Testing
- Cross-tenant access tests: user A cannot read/write user B's data.
- Automated test in CI for every new table.

## Forbidden
- Application-only tenant filtering.
- Shared caches without tenant keys.
- Cross-tenant aggregations without explicit authorization.
