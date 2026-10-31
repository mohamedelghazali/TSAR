# WebSocket Security

## Handshake
- `Origin` header strictly validated against an allow-list.
- Authentication required at handshake; token in header, not query string.
- CSRF protection for cookie-based authentication; prefer token-based.
- Reject cross-origin handshakes by default.

## Transport
- `wss://` only; `ws://` forbidden.
- TLS 1.3 with certificate verification.
- HSTS applied to the web origin.

## Messages
- Schema validation on every message.
- Size limit per message and per connection.
- Rate limit per connection and per user.
- Binary messages validated against expected content type.

## Session
- Idle timeout (<= 30 minutes).
- Reauthenticate on sensitive actions even after handshake.
- Revoke sessions on logout; close sockets.

## Authorization
- Enforce on every message; handshake authorization is not sufficient for long-lived connections.
- Re-check role changes; disconnect on privilege revocation.

## Forbidden
- Token in query string.
- Accepting connections from unlisted origins.
- Unbounded message sizes.
