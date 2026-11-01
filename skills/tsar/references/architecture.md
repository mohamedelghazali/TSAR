# TSAR Architecture Reference

This is a navigation guide. The upstream repository and its current `manifest.yaml` remain authoritative.

## Repository map

| Path | Role |
|---|---|
| `system/` | Core directives, prohibited patterns, enforcement levels, lifecycle |
| `rules/` | Security rules organized by domain |
| `prompts/` | Agent-specific and universal instruction packs |
| `policies/` | OPA/Rego and Cedar policy artifacts |
| `skills/` | Security helpers and scanners in the TSAR project |
| `tools/` | CLI, orchestrator, reporting, LSP, dashboard |
| `integrations/` | CI/CD templates and hooks |
| `examples/` | Secure examples and anti-pattern demonstrations |
| `docs/` | Architecture, setup, agent integration, compliance mappings |
| `tests/` | Automated verification suite |

## Core operating model

TSAR describes a layered security-governance approach:

1. Generation-time guidance through agent instruction files.
2. Local verification through scanners and project hooks.
3. CI governance through automated repository checks and policy validation.
4. Human review for design flaws, business-logic risks, and residual uncertainty.

Prompt guidance alone is not deterministic enforcement. Use controls appropriate to the risk.

## Important entry points

- `manifest.yaml`: current rule inventory, lifecycle metadata, and active file references.
- `system/CORE_DIRECTIVE.md`: core governing directive.
- `system/DO_NOT_GENERATE.md`: prohibited generation patterns.
- `system/ENFORCEMENT_LEVELS.md`: enforcement model.
- `system/LIFECYCLE.md`: lifecycle and update behavior.
- `prompts/universal.md`: generic agent instructions.
- `docs/architecture.md`: architecture documentation.
- `docs/agent-integration.md`: integration guidance.
- `docs/agent-compatibility-matrix.md`: supported agent instruction formats.
- `verify-all.sh`: repository-wide verification entry point.

## Version discipline

Do not hard-code an assumed current version in generated reports or integrations. Read `VERSION`, `manifest.yaml`, and release qualification documentation, and flag any disagreement between version declarations rather than silently resolving it.
