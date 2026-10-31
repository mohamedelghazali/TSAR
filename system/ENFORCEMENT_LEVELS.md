# Enforcement Levels

| Level | Behavior |
|---|---|
| Strict (default) | Refuse unsafe generation; require secure alternative. |
| Warn | Generate but prepend a security warning with the violated rule. |
| Advisory | Used only when manifest cannot be fetched; output marked for manual review. |

Strict mode is mandatory for: authentication, cryptography, payments, health data, children's data, and any system handling government identifiers.
