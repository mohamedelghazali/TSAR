# TSAR Security Model

## Threat Model
TSAR assumes:
- The AI agent is honest but fallible.
- User inputs are untrusted.
- Tool outputs and retrieved documents are untrusted.
- Upstream standards may change and must be tracked.
- The network may be partitioned (offline fallback required).

TSAR does not assume:
- The agent will always follow instructions.
- The user will not attempt prompt injection.
- The repository will stay unchanged.

## Defense Layers
1. **Policy layer**: `system/CORE_DIRECTIVE.md`, `DO_NOT_GENERATE.md`.
2. **Rule layer**: `rules/` provides category-specific controls.
3. **Enforcement layer**: scanners block unsafe output.
4. **Integration layer**: CI/CD and pre-commit hooks.
5. **Lifecycle layer**: manifest versioning and auto-update.

## Failure Modes
| Failure | Detection | Response |
|---|---|---|
| Agent ignores rules | Scan finds violation | Block commit, reopen prompt |
| Manifest unreachable | `tsar version` fails | ADVISORY mode, manual review |
| Rule outdated | Upstream standards changed | Auto-update opens PR |
| Scanner false negative | Not detected | Complementary SAST required |
| Malicious tool output | Provenance tagging | Treated as data, not instruction |

## Non-Goals
- TSAR is not a runtime WAF.
- TSAR is not a substitute for code review.
- TSAR cannot prove absence of vulnerabilities.
