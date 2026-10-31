# gRPC Security

## Transport
- TLS 1.3 with mTLS for service-to-service.
- Server certificate verified against a known CA or SPKI pin.
- No plaintext gRPC in production.

## Authentication
- Bearer tokens in metadata (short-lived).
- mTLS for workload identity (SPIFFE or equivalent).
- No credentials in message bodies.

## Authorization
- Interceptor enforces per-method authorization.
- Object-level checks in handlers.
- Reflect the caller identity from the verified certificate, not from metadata.

## Input Validation
- Protobuf strict mode; reject unknown fields.
- Limit message size (server-side).
- Timeouts on all calls.

## Rate Limits
- Per-caller, per-method.
- Circuit breakers for downstream calls.

## Reflection
- Disabled in production unless authenticated and authorized.

## Forbidden
- `grpc.WithInsecure()` in production.
- Reflection exposed publicly.
- Metadata used for authorization without verification.
