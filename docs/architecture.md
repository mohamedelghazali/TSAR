# TSAR Architecture

## Purpose
TSAR is a security governance layer for AI-generated code. It enforces rules at generation time, verifies them at commit time, and monitors them at runtime.

## Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  L1 — Policy Layer (system/)                                    │
│  CORE_DIRECTIVE.md · DO_NOT_GENERATE.md · ENFORCEMENT_LEVELS.md │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  L2 — Rules Layer (rules/)                                      │
│  crypto · owasp-llm · owasp-web · agentic-ai · ai-models        │
│  platform · hardware · data · cloud · containers · api · iam    │
│  supply-chain · messaging · database · observability · secrets  │
│  networking · compute · testing · governance · privacy          │
│  threat-intel · forensics · identity-federation · email         │
│  endpoint · backup · disaster-recovery · legal-hold             │
│  application-security · infrastructure · development · emerging │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  L3 — Enforcement Layer (skills/ + tools/)                      │
│  secret-scanner · secure-review · crypto-inventory              │
│  threat-modeler · tsar-cli · tsar-orchestrator · tsar-report    │
│  tsar-lsp · tsar-web                                            │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  L4 — Integration Layer (integrations/ + prompts/)              │
│  GitHub Actions · GitLab CI · Bitbucket · Azure DevOps          │
│  pre-commit hooks · 15 agent prompts                            │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  L5 — Lifecycle Layer (manifest.yaml + .github/workflows/)      │
│  Version pinning · auto-update · drift detection · validation   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### At Agent Generation Time
1. Agent fetches `manifest.yaml` and reads `active_files`.
2. Agent applies `CORE_DIRECTIVE.md` and relevant rules.
3. Agent generates code that satisfies all applicable rules.
4. Agent runs secret scanner and secure review mentally (or via skill calls).
5. Agent emits code with rule citations where non-obvious.

### At Commit Time
1. Pre-commit hook runs `secret-scanner` and `secure-review` on staged files.
2. Blocks commit on any HIGH finding or secret.
3. `lint_rules` validates the manifest.

### At CI Time
1. Orchestrator runs all steps in parallel.
2. Emits JSON/Markdown report.
3. Blocks merge on HIGH findings.
4. Uploads artifacts for audit.

### At Runtime
1. Application uses secure patterns from `examples/secure/`.
2. EDR/runtime policies reference `rules/containers/runtime-security.md`.
3. SIEM consumes audit logs redacted per `rules/data/logging-redaction.md`.

### Lifecycle
1. GitHub Actions daily fetch upstream standards.
2. Compares hashes with `.tsar-cache/`.
3. Bumps manifest version; opens PR.
4. Team reviews and merges.
5. Agents pick up new version at next session.

## Trust Boundaries

| Boundary | Trust Level | Controls |
|---|---|---|
| Agent ↔ User | Untrusted input | Prompt injection defenses |
| Agent ↔ Rules | Trusted ruleset | Manifest versioning, signature verification |
| CI ↔ Repository | Trusted | OIDC identity, SBOM |
| Runtime ↔ Secrets | Trusted only if verified | Vault/KMS, fail-closed |
| External ↔ Internal | Untrusted | WAF, mTLS, rate limits |

## Design Principles

1. **Fail closed**: if rules cannot load, refuse to generate for Tier-1.
2. **Structural over semantic**: prompts separated by role, not concatenated.
3. **Defense in depth**: multiple layers, no single point of failure.
4. **Time-bound exceptions**: every suppression has an expiry.
5. **Evidence-driven**: every control produces auditable evidence.
6. **Portable**: works with 15 agents without vendor lock-in.
7. **Testable**: every rule has a test in `tests/`.

## Extension Points

- **New rule**: add file in `rules/`, reference in `manifest.yaml`, add test.
- **New skill**: add directory in `skills/`, implement `SKILL.md` and script.
- **New agent**: add prompt in `prompts/`, update compatibility matrix.
- **New integration**: add pipeline template in `integrations/`.
- **New compliance framework**: add mapping in `docs/compliance/`.

## Failure Modes

| Failure | Detection | Response |
|---|---|---|
| Manifest unreachable | `tsar drift` fails | ADVISORY mode; refuse Tier-1 |
| Rule outdated | Upstream hash changed | Auto-update PR |
| Agent ignores rules | Scanner finds violation | Block commit; re-prompt |
| Scanner false negative | Not detected | Complementary SAST required |
| Tool output poisoned | Provenance tagging | Treated as data |
| Compromised agent | Anomalous commits | Disable, review, re-enable with strict mode |
