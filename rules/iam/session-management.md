# Session Management

## Session IDs
- CSPRNG-generated, >= 128 bits entropy.
- Stored in `HttpOnly`, `Secure`, `SameSite=Strict` cookies.
- `__Host-` prefix to prevent cookie tossing.

## Rotation
- Rotate session ID on login.
- Rotate on privilege change.
- Rotate on sensitive actions (password change, email change).

## Lifetime
- Idle timeout <= 30 minutes for admin, <= 2 hours for users.
- Absolute timeout <= 12 hours regardless of activity.
- Refresh tokens: rotate on each use; detect reuse and revoke the family.

## Revocation
- Logout revokes server-side; not just client cookie deletion.
- Password change revokes all sessions.
- Role change re-evaluates permissions in the current session.

## Concurrency
- Limit concurrent sessions per user (configurable, default 5).
- Show active sessions in account settings; allow user-initiated revocation.

## Forbidden
- Session IDs in URLs.
- Predictable session IDs.
- Sessions that survive password change.
