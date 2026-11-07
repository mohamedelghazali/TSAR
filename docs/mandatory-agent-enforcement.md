# Mandatory Agent Adoption and Enforcement Contract

## Purpose

This contract defines how a supported agent integration must apply TSAR before, during, and after engineering work. It closes the gap between making TSAR instructions available and proving that an integration actually invoked the policy and verification steps.

The contract is an integration boundary, not a claim that TSAR can change model weights, override provider system instructions, or force arbitrary closed models to comply. Enforcement is only claimed for execution paths controlled by an adapter, runtime, repository hook, or CI gate.

## Enforcement levels

| Level | Integration capability | What TSAR may claim |
|---|---|---|
| E0 — Reference only | User or agent can read TSAR documentation | Guidance is available; no execution enforcement |
| E1 — Instruction bootstrap | Agent project/global instructions point to TSAR | Bootstrap is configured; loading and compliance are not guaranteed |
| E2 — Preflight adapter | A controlled adapter invokes the pinned upstream verifier before task execution and blocks on failure | Preflight is enforced on that adapter path |
| E3 — Tool boundary | The adapter checks tool/action requests against the task policy and authorization scope before dispatch | Covered tool calls are gated; uncovered tools are not |
| E4 — Output/commit gate | Generated changes are scanned and policy checks run before acceptance or merge | Covered repository changes are gated by the configured checks |
| E5 — Attested lifecycle | Required review gates are supported by verifiable evidence and authorized reviewer attestations | The recorded lifecycle gates are evidenced; this does not prove absence of all vulnerabilities |

An integration must report its actual highest level and the specific paths covered. Levels are cumulative only when every preceding requirement is met.

## Required adapter lifecycle

### 1. Bootstrap and identity

Before starting a security-sensitive engineering task, the adapter MUST:

1. Identify the agent/runtime and its integration mode.
2. Resolve the authoritative TSAR repository and immutable commit SHA.
3. Fetch and validate the manifest and all four core directives from that same commit.
4. Validate repository identity, manifest schema, strict mode, and fail-closed settings.
5. Select applicable domains from the manifest. Heuristic selection may propose domains, but the adapter must permit explicit operator overrides and must not silently omit an explicitly selected domain.
6. Stop the controlled task path if required policy cannot be fetched, validated, or pinned.

A branch name such as `main` is a discovery reference, not immutable provenance. Every policy file used for one task must resolve to the same recorded commit SHA.

### 2. Policy context

The adapter MUST provide the model with the verified policy context before implementation begins. The context MUST identify:

- TSAR repository and immutable commit SHA.
- Manifest version and manifest SHA-256.
- Four core directive paths and their content hashes.
- Applicable domain names, rule paths, and content hashes.
- The enforcement level actually active.
- Any policy files that could not be loaded and the resulting blocked/degraded state.

Do not report a policy file as loaded merely because its URL or path was supplied to the model.

### 3. Tool/action boundary

Where an integration controls tool dispatch, it SHOULD classify each proposed action before execution. At minimum, the adapter must distinguish read-only inspection, repository modification, external network access, credential/secret access, deployment, and irreversible actions.

The adapter MUST enforce the user's authorization and the platform's permission boundary independently of TSAR. TSAR policy cannot grant permissions the user or platform did not grant. High-impact or irreversible actions require the explicit approval required by the host platform and the applicable TSAR rules.

If the integration cannot intercept tool calls, it MUST report E3 as unsupported rather than imply runtime enforcement.

### 4. Output and change verification

Before accepting generated code or a repository change, the integration MUST run the configured deterministic checks over the actual changed content, not merely the model's explanation. At minimum:

- Secret scanning over changed files.
- Secure code review/scanning over changed files.
- Relevant repository tests and policy checks.
- A clear non-zero result when a blocking check fails.

A scanner pass is not a proof of vulnerability absence. Logic flaws, threat-model gaps, and false negatives still require appropriate human review.

### 5. Evidence

For each controlled task, the adapter SHOULD emit a machine-readable record containing:

- Task/run identifier and timestamp.
- Agent/runtime and adapter version.
- TSAR commit SHA, manifest version/hash, and loaded policy hashes.
- Selected domains and enforcement level.
- Checks executed, versions, exit codes, and artifact hashes.
- Checks skipped, with explicit reasons.
- Gate decisions and reviewer identity where applicable.

Evidence MUST distinguish observed execution from requested or planned execution. A local JSON record is not a signed attestation or tamper-proof audit log. Use the lifecycle evidence and reviewer-signature facilities when authenticated review evidence is required.

## Fail-closed behavior

For a controlled security-sensitive task path, the adapter MUST block implementation when:

- The upstream commit cannot be pinned.
- The manifest or required core directives fail validation.
- The manifest requests strict/fail-closed behavior and required policy cannot be loaded.
- The selected domain rules are missing or inconsistent.
- A mandatory blocking check fails.

The adapter may provide non-executable explanatory guidance about the failure, but must not silently downgrade to advisory mode or label the task compliant.

## Conformance tests

An adapter claiming E2 or higher MUST provide automated tests demonstrating:

1. A valid immutable TSAR snapshot is loaded and its SHA is recorded.
2. A changed manifest or policy file changes the recorded hash.
3. An unavailable manifest or missing core directive blocks the task.
4. A stale or mixed-commit policy set is rejected.
5. An explicitly selected unknown domain is rejected.
6. A failed secret/security check blocks acceptance.
7. A skipped check is reported as skipped, never passed.
8. A tool action outside the user's authorization is denied by the host boundary.
9. Evidence records distinguish PASS, FAIL, BLOCKED, and NOT_RUN.
10. The adapter reports unsupported enforcement capabilities honestly.

A conformance test suite must test the adapter's real invocation path. Unit tests of a helper function alone do not establish that the host agent actually calls the adapter.

## Compatibility reporting

Every supported-agent entry must state:

- Integration mechanism and supported product/runtime versions.
- Whether bootstrap is automatic, project-scoped, global, or manual.
- Whether preflight is automatically invoked.
- Whether tool calls can be intercepted.
- Whether output checks are mandatory.
- What evidence is produced.
- Known limitations and the verified enforcement level.

A prompt file, Agent Skill, MCP tool description, or repository instruction file alone is E0/E1. It is not E2+ unless the host integration demonstrably invokes and enforces the corresponding control.

## Current TSAR implementation boundary

The repository provides policy files, agent instructions and skills, an immutable upstream preflight verifier, the `tsar agent-gate` launch adapter, a reusable `ToolBoundary` dispatch API, lifecycle planning and initialization, local scanning, repository CI, and signed lifecycle evidence primitives. Automated tests cover the CLI launch gate and the reusable dispatch boundary.

The current E2 claim applies only to commands launched through `tsar agent-gate`. The `ToolBoundary` API is an E3 building block, not proof that any named provider integration intercepts every tool call. A host integration must register tools in trusted code, supply authenticated identity/scopes, verify action-bound approvals, persist audit events, route every covered invocation through the boundary, and pass host-level bypass/conformance tests before E3 can be claimed for that integration. Closed or chat-only model products that expose no supported pre-execution or tool-dispatch integration remain outside TSAR's direct enforcement boundary.
