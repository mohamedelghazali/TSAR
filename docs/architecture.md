# TSAR Architecture

## Purpose

TSAR is a security governance layer for AI-assisted software development. It provides structured security rules and agent instructions, then checks code through local tools and repository automation. It is designed to reduce security defects—not to guarantee that every vulnerability is prevented.

## Layers

    L1 — Policy Layer (system/)
         Core directive, prohibitions, enforcement levels
                         |
                         v
    L2 — Rules Layer (rules/ + manifest.yaml)
         37 domains, 171 active rule files, versioned inventory
                         |
                         v
    L3 — Agent Guidance (prompts/)
         15 agent-specific instruction packs + universal fallback
                         |
                         v
    L4 — Verification (skills/ + tools/)
         Secret scanning, secure review, CLI, orchestrator, reports
                         |
                         v
    L5 — Repository Governance (integrations/ + .github/)
         Hooks, CI checks, policy validation, audit artifacts

## Data Flow

### During AI-Assisted Development
1. The developer installs the instruction file for the selected agent.
2. The instructions identify TSAR's manifest and relevant security rules.
3. The agent is asked to apply those rules while generating or modifying code.
4. The developer runs TSAR scanners and reviews findings.

Agent instructions are a guidance layer. They cannot force a provider or model to comply and must not be treated as a security boundary.

### At Commit and CI Time
1. Local hooks can run scanners against staged files.
2. Rule linting and manifest validation detect repository consistency issues.
3. CI workflows run tests, scanners, policy checks, and infrastructure schema/static validation.
4. Required checks can block pull-request merges when configured in GitHub.

### Runtime

TSAR is not itself a runtime monitoring daemon, WAF, EDR, or SIEM. Runtime controls described by individual rules must be implemented in the target application or infrastructure and monitored by the team's chosen runtime security products.

## Trust Boundaries

| Boundary | Risk | TSAR / deployment control |
|---|---|---|
| Agent ↔ User | Untrusted input and prompt injection | Applicable LLM and agentic-AI rules |
| Agent ↔ Rules | Stale or unavailable instructions | Versioned manifest and local vendoring |
| CI ↔ Repository | Unreviewed or unsafe changes | Protected branch and required checks |
| Application ↔ Secrets | Credential exposure | Secret scanning and platform secret stores |
| External ↔ Internal | Network and API threats | Apply relevant WAF, mTLS, auth, and zero-trust controls |

## Design Principles

1. **Fail closed where configured**: critical workflows should fail when required rules cannot be loaded.
2. **Defense in depth**: combine agent guidance, scanners, hooks, CI, and human review.
3. **Time-bound exceptions**: document suppressions and set expiry dates.
4. **Evidence-driven**: retain CI logs and reviewable reports.
5. **Portable**: keep rules and integrations usable across development tools.
6. **Testable**: validate rule files, manifests, scanners, and integrations.

## Extension Points

- **New rule**: add a file under rules/, reference it in manifest.yaml, and add suitable tests.
- **New agent**: add an instruction file under prompts/ and update the compatibility matrix.
- **New integration**: add a pipeline template under integrations/.
- **New compliance framework**: add a mapping under docs/compliance/.

## Failure Modes

| Failure | Detection | Response |
|---|---|---|
| Manifest unreachable | Lifecycle or drift check fails | Use a reviewed local copy or fail closed |
| Rule outdated | Version/hash comparison | Review and merge an update |
| Agent ignores instructions | Scanner or reviewer finds a violation | Reject the change and correct integration |
| Scanner false negative | Not detected by current checks | Add complementary SAST and human review |
| External tool output is poisoned | Untrusted content reaches agent | Treat tool output as data, not instructions |
| Compromised agent | Suspicious generated changes | Disable integration and investigate |
