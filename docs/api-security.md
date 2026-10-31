# API Security Guide

## Choose the Right Protocol
| Protocol | Use | Rules |
|---|---|---|
| REST | General | rules/api/rest.md |
| GraphQL | Flexible queries | rules/api/graphql.md |
| gRPC | Service-to-service | rules/api/grpc.md |
| WebSocket | Real-time | rules/api/websocket.md |

## Common Requirements
- Auth on every request; no anonymous access to sensitive endpoints.
- Object-level authorization.
- Schema validation on input; strict reject on unknown fields.
- Rate limits per identity and per endpoint.
- Structured error responses; no stack traces.
- TLS 1.3 with certificate verification.
- Idempotency keys for unsafe operations (payments, transfers).

## Verification Checklist
- [ ] Auth verified server-side.
- [ ] Authorization enforced per object.
- [ ] Input schema strict.
- [ ] Output sanitized.
- [ ] Rate limits configured.
- [ ] Logs redact PII and secrets.
- [ ] TLS 1.3 with HSTS.
