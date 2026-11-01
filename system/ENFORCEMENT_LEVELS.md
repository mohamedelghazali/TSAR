# Enforcement Levels

| Level | Behavior |
|---|---|
| Strict (default) | Refuse unsafe generation; require a secure alternative. This is the active default. |
| Warn | Generate only when the current project configuration and applicable rule explicitly permit warning-only handling; report the finding and do not bypass hard stops. |
| Advisory | Disabled by the current manifest. May be used only when `enforcement.allow_advisory_fallback: true` and `lifecycle.fail_closed: false`; otherwise stop security-sensitive implementation when required policy context is unavailable and mark TSAR review incomplete. |

Strict mode is mandatory for authentication, cryptography, payments, health data, children's data, government identifiers, production infrastructure, and other high-impact systems.

The current `manifest.yaml` sets `lifecycle.fail_closed: true` and `enforcement.allow_advisory_fallback: false`. Therefore, a missing or unreadable manifest or required rule file is not permission to proceed in Advisory mode. Do not infer an exception or silently change these settings.
