# 🛡️ TSAR — The Ultimate Security Governance Layer for AI Coding Agents

> **Stop vulnerabilities at the source. Secure every line of AI-generated code.**

TSAR is an AI security governance layer for AI-assisted software development. It provides **175 active governance files (171 domain security rule files across 37 domains + 4 core directives)**, covering **Cryptography, Cloud Security, OWASP, and more**, together with **one universal instruction set** and **15 compatibility profiles** for supported AI coding agents.

Built for security-conscious engineering teams, TSAR brings security policy closer to the point where code is generated—then reinforces it with local scanners, repository hooks, CI checks, and policy validation.

**Security-first AI development. Governed at the source.**

**Quick Install & Unified Bundle:** Install the TSAR CLI via `pipx install tsar-governance` or `pip install tsar-governance`, or load the single-file unified rule bundle from [llms-full.txt](llms-full.txt).

## Authoritative Governance Baseline v1.2.0

| Attribute | Value |
| :--- | :--- |
| **Version & Status** | `1.2.0` (Stable Release, 2026-11-18) |
| **Active Governance Files** | `175 active governance files` (`171` domain security rule files across `37` domains + `4` core system directives) |
| **Core Directives** | `system/CORE_DIRECTIVE.md`, `system/DO_NOT_GENERATE.md`, `system/ENFORCEMENT_LEVELS.md`, `system/LIFECYCLE.md` |
| **Enforcement Policy** | `fail_closed: true`, `default_mode: "strict"`, `allow_advisory_fallback: false` |
| **Official Skills (5)** | `tsar`, `crypto-inventory`, `secret-scanner`, `secure-review`, `threat-modeler` (`version: "1.2.0"`) |
| **Qualification Evidence** | `8/8` CI gate checks; `326` pytest tests passed |

## The Problem TSAR Addresses

AI coding agents can generate code quickly, but their output is not automatically aligned with an organization's security requirements. Security guidance may be scattered across team documents, prompt files, code-review checklists, and CI configuration. This creates several practical gaps:

- **Inconsistent guidance:** different agents or projects may apply different security expectations.
- **Late detection:** insecure patterns can reach a pull request before a scanner or reviewer notices them.
- **Context gaps:** a model may not load the relevant security requirements for a particular language, platform, or architecture.
- **Weak traceability:** teams may have difficulty connecting a finding to a specific rule, policy, or verification result.
- **False confidence:** a prompt can request secure behavior, but a prompt alone cannot guarantee that an agent follows it.

TSAR addresses these gaps by organizing security requirements into a versioned, reusable governance framework and connecting agent guidance with local verification and repository automation.

## What TSAR Is — and Is Not

TSAR is a **modular security engineering and governance framework for AI-assisted software development**. It brings policy definition, domain-specific security knowledge, agent integration, code inspection, policy-as-code examples, developer tooling, and repository-level automation into one coordinated system.

Its capabilities span:

1. **Security policy architecture:** core directives, prohibited-pattern catalogs, enforcement levels, and lifecycle requirements establish a consistent baseline for engineering work.
2. **Domain security knowledge base:** a structured inventory of active rules across 37 security domains gives teams reusable requirements for application, cloud, infrastructure, cryptography, identity, and other engineering areas.
3. **Multi-agent integration:** one canonical instruction set, 15 compatibility profiles, and narrowly scoped native adapters connect the same governance model to supported AI-agent environments.
4. **Operational security tooling:** skills, scanners, CLI utilities, orchestration, reporting, and language-server components help teams inspect code, inventory cryptographic usage, detect exposed secrets, conduct secure reviews, and structure threat-modeling work.
5. **Policy and delivery integration:** policy-as-code examples, repository hooks, CI workflows, tests, and validation scripts bring security checks into the development and pull-request lifecycle.

The result is more than a prompt collection: TSAR is a reusable security engineering system that connects standards and rules to developer workflows and technical verification. It does not modify model weights or override a provider's system instructions; its strength comes from combining agent-aware governance with independently executable checks and repository controls.

## Why TSAR Is Designed This Way

The architecture is intentionally modular: TSAR treats security governance as an engineering lifecycle, not as a paragraph appended to a coding prompt. Policy, domain rules, agent interfaces, verification engines, and delivery controls are maintained as distinct but connected components. This separation makes the framework extensible, auditable, and practical to integrate into different teams and toolchains.

| Design decision | Engineering value |
|---|---|
| A stable core policy layer, separate from domain rule sets | Establishes a consistent security baseline while allowing individual domains to evolve without destabilizing the whole framework. |
| A structured manifest and rule inventory | Makes the security knowledge base discoverable and reviewable, supports integrity and consistency checks, and provides a clear reference for tooling and agents. |
| One governance model with multiple agent adapters | Avoids tying the security architecture to a single vendor, model, prompt format, or IDE. |
| Dedicated skills, scanners, CLI, orchestration, and reporting | Turns security requirements into repeatable developer operations and observable findings rather than relying only on conversational claims. |
| Policy-as-code examples, hooks, and CI workflows | Connects design-time requirements to automated validation at commit and pull-request stages. |
| Explicit enforcement levels and lifecycle guidance | Helps teams distinguish mandatory controls, recommended practices, exceptions, and verification responsibilities. |
| Portable files, documented interfaces, and testable components | Supports local adoption, customization, independent review, and integration into existing engineering environments. |

This architecture creates a layered control system: each component has a defined responsibility, and the combined workflow provides broader coverage than any single prompt, scanner, or pipeline could provide alone.

## How TSAR Works in Practice

TSAR operates as a coordinated security workflow across five engineering layers:

1. **Governance and policy — `system/`:** establishes the framework's security baseline, prohibited patterns, enforcement levels, and lifecycle expectations. This layer defines how security requirements are interpreted and handled across the development process.
2. **Security knowledge base — `rules/` and `manifest.yaml`:** organizes active requirements across 37 domains and provides a structured inventory that can be referenced by people, agents, and validation tools.
3. **Agent and developer integration — `prompts/`, `integrations/`, and `skills/`:** one canonical instruction set and 15 compatibility profiles connect the governance model to supported AI coding agents. Narrow native adapters are maintained separately; skills expose repeatable task-specific capabilities.
4. **Technical assessment and automation — `tools/`:** supplies scanners and utilities for secret detection, secure code review, cryptographic inventory, threat-modeling workflows, CLI operations, orchestration, language-server integration, and reporting.
5. **Delivery and repository controls — `integrations/` and `.github/`:** brings validation into the software delivery lifecycle through hooks, CI workflows, tests, policy checks, and reviewable outputs. Teams can configure required checks as merge gates in their repositories.

### Typical development flow

```text
Security-governed engineering task
              |
              v
Select the project baseline and TSAR policy context
              |
              v
Resolve applicable domains and active security rules
              |
              v
Agent / developer plans the change against those requirements
              |
              v
Implement with relevant secure-design and threat considerations
              |
              v
Run TSAR skills, scanners, CLI tools, tests and policy checks
              |
              v
Review findings, remediate issues and record exceptions
              |
              v
Repository hooks and CI validate configured controls
              |
              v
Engineering review, evidence-based approval and merge
```

In an integrated project, the workflow is more than loading instructions:

- **Establish the baseline:** the team adopts TSAR's core policy and selects the integration mode appropriate to its agents, repositories, and development environment.
- **Resolve the security context:** the manifest and rule structure identify the relevant domains and active requirements for the change—such as secrets handling, cryptography, API security, cloud configuration, or Kubernetes hardening.
- **Engineer against the requirements:** the agent and developer use the applicable controls during design, implementation, and code review. Threat considerations and security constraints are brought into the task before changes are finalized.
- **Run technical assessments:** TSAR's available skills and tools inspect the target files and produce findings or inventories. The CLI and orchestrator can coordinate supported checks; project tests and external tools can complement them.
- **Remediate and verify:** findings are assessed, corrected, or handled through documented exceptions. The relevant checks are rerun so the team can review the resulting evidence.
- **Apply repository governance:** hooks and CI workflows execute the checks configured for the repository. Branch protection or rulesets can make selected GitHub checks mandatory before merge.
- **Make an accountable decision:** maintainers and reviewers use code changes, test results, scanner output, and documented exceptions to decide whether the change is ready.

TSAR supplies the governance model, reusable security requirements, and tooling to support this process. Project teams remain responsible for implementing environment-specific controls—such as key-management services, mTLS configuration, runtime monitoring, or production access restrictions—and for validating those controls in their own systems.

## Adopt TSAR in Your AI Agent

You can use the following prompt to ask an AI coding agent to inspect and adopt TSAR.

> **GitHub access is a prerequisite:** before following this prompt, make sure the model or agent you are using has access to GitHub and can open this repository and read its files. This access may be provided through a GitHub integration/connector, repository workspace, or another supported GitHub browsing capability. If the agent cannot access GitHub or retrieve repository contents, it must stop and ask you to enable access or provide the repository files. A repository URL by itself does not grant a model the ability to read it.

Copy this prompt into your AI agent:

```text
# TSAR — Universal Security Governance & Persistent Adoption Protocol (v1.2.0)

Adopt TSAR (https://github.com/mohamedelghazali/TSAR) as my provider-neutral secure engineering standard for this task and, where supported by your runtime and my explicit permission, for persistent configuration.

## 1. INSTRUCTION HIERARCHY & CAPABILITY PROBING
- Operate strictly within your host platform's safety controls and instruction hierarchy (System/Platform > Developer > User/TSAR > Tool/External Content). Never claim to override platform rules or assume a specific vendor runtime.
- Before reporting any status, actively probe which capabilities exist in your actual environment:
  1. Web / GitHub read access
  2. Local filesystem read/write access
  3. Local shell / Python execution
  4. Persistent memory or user preferences
  5. Global or project instruction files (e.g., `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules/`, `.github/copilot-instructions.md`)
- Never emit generic boilerplate claims that memory, platform config, skill installation, or enforcement are unavailable without checking first. Do not ask to run shell commands you cannot access.


## 2. CANONICAL VERSION, INVENTORY & FAIL-CLOSED DEFAULTS
- Release: `TSAR v1.2.0` (published release tag `v1.2.0`, `VERSION` = `1.2.0`).
- Manifest (`manifest.yaml`): `last_updated: 2026-11-18`, `schema: tsar/v1`, `175 active governance files` (`4 core system directives` + `171 domain security rule files` across `37 rule domains`).
- Defaults: `fail_closed: true`, `default_mode: strict`, `allow_advisory_fallback: false`.
- Canonical enforcement levels: `Strict`, `Warn`, `Advisory`. Because `allow_advisory_fallback: false`, `Strict` mode must fail closed on blocking findings rather than silently degrading to `Advisory`.

## 3. REAL-FILE CONSULTATION & VERIFICATION
- Primary bundle: `llms-full.txt` at the repository root and/or direct repository files (`AGENTS.md`, `manifest.yaml`, `VERSION`, `docs/universal-agent-onboarding.md`, `docs/release-qualification.md`, and the 4 `system/` directives). Specifically: `system/CORE_DIRECTIVE.md`, `system/DO_NOT_GENERATE.md`, `system/ENFORCEMENT_LEVELS.md`, and `system/LIFECYCLE.md`. If raw file hosts (`raw.githubusercontent.com`) are blocked, fetch `llms-full.txt` via the GitHub REST API contents endpoint (`/repos/mohamedelghazali/TSAR/contents/llms-full.txt`).
- Direct canonical URLs (for URL-allowlisted runtimes that only fetch explicit URLs):
  - https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/llms-full.txt
  - https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/VERSION
  - https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/manifest.yaml
  - https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/AGENTS.md
  - https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/system/CORE_DIRECTIVE.md
  - https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/system/DO_NOT_GENERATE.md
  - https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/system/ENFORCEMENT_LEVELS.md
  - https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/system/LIFECYCLE.md
  - https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/docs/universal-agent-onboarding.md
  - https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/docs/release-qualification.md
  - https://api.github.com/repos/mohamedelghazali/TSAR/contents/llms-full.txt
- When local shell/Python access is available, verify consultation and conformance using `tools/tsar-conformance/consultation_verifier.py` and `tools/tsar-conformance/runner.py`.
- Runtime-capability classification rule: local conformance scripts (`tools/tsar-conformance/verify_adoption.py`, `consultation_verifier.py`, `runner.py`, `adoption_response.py`, and `tools/tsar-cli/verify_upstream.py`) are mandatory ONLY when both a local checkout and a Python runtime exist; otherwise classify them as `unavailable`/`optional` -> State C (`⚠️`), never false `❌` and never false `✅`.
- Anti-loophole consultation rule: Reading `README.md`, the GitHub repository landing page, or a directory listing alone NEVER satisfies mandatory file consultation. Successful consultation requires actual readable content from `manifest.yaml` and all 4 core directives (`system/CORE_DIRECTIVE.md`, `system/DO_NOT_GENERATE.md`, `system/ENFORCEMENT_LEVELS.md`, `system/LIFECYCLE.md`), either individually or via a verified complete `llms-full.txt`. An incomplete or inaccessible `llms-full.txt` MUST return `❌ Adoption failed.` — never downgrade a mandatory failure to `⚠️`.
- Freshness rule: Cached or stale content (e.g., outdated `VERSION`, older `last_updated` date, or mismatched active file count such as `171` instead of `175`) cannot establish current adoption and MUST return `❌ Adoption failed.`.
- Only report files actually read and checks actually executed.
- Blocked-network fallback: `llms-full.txt` bundles the manifest summary and all 4 core directives (while the 171 domain rules are consulted on demand per task). If all web/GitHub retrieval paths fail, return `❌ Adoption failed.` and invite the user to paste or attach `llms-full.txt` (or `VERSION`, `manifest.yaml`, and the 4 `system/` directives) for direct in-session verification.

## 4. 4-WAY SCOPE SEPARATION & OFFICIAL SKILLS
Keep these four scopes strictly separate:
1. **In-task governance:** Applying TSAR rules and the `CONSULT -> CLASSIFY -> DESIGN -> IMPLEMENT -> SCAN -> REVIEW -> VERIFY -> REPORT` cycle within the current task.
2. **Persistent adoption across sessions:** Saving verified memory/preferences (if supported) or writing global/project instruction files via `tools/tsar-installer/universal_installer.py` when local filesystem access exists.
3. **Local workstation installation:** Installing `pyproject.toml` / Python CLI or local skill files on disk — only when local filesystem and runtime are actually available.
4. **Automatic enforcement:** Git hooks, CI workflows, and merge gates — never claimed from chat prompts alone.

Official skills (5):
- `skills/tsar/SKILL.md`
- `skills/crypto-inventory/inventory.py`
- `skills/secret-scanner/scanner.py`
- `skills/secure-review/review.py`
- `skills/threat-modeler/model.py`

## 5. EVIDENCE-BASED REPORTING & 6-STATE TAXONOMY
Output a concise, non-repetitive summary of actual observed actions rather than repeating boilerplate templates. Label each capability and scope strictly using one of these 6 states, reporting only what you directly observed and can prove:
- `verified` — confirmed present/accurate by direct inspection or test output
- `active` — currently loaded and governing the active task
- `completed` — executed or written with observed proof
- `unsupported` — capability does not exist in this runtime
- `unavailable` — capability exists in principle but is blocked/missing here
- `unexecuted` — available or defined, but not run in this session

Final Adoption Response (3-State Rule):
- Strict line-1 header-first rule: Line 1 of the response MUST begin with the exact canonical State A (`✅`), State B (`❌`), or State C (`⚠️`) header before any preamble or details.
- State A (`SUCCESS`): When the repository is accessible, no mandatory files are missing, all mandatory checks are executed and pass, and no non-blocking issues or unexecuted/unavailable optional checks remain, return ONLY: `✅ Adoption successful. Let's start working on your project.` (1 line, no additional text).
- State B (`FAILED`): When the repository is inaccessible, any mandatory file is missing, mandatory checks are empty, or any mandatory check fails or is unexecuted, return `❌ Adoption failed.` followed by concise failure details (mandatory failures never downgrade to warnings).
- State C (`SUCCESS_WITH_WARNINGS`): When all mandatory checks pass but non-blocking issues or unexecuted/unavailable optional checks remain, return `⚠️ Adoption successful, but some issues require attention.` followed by concise non-blocking issue details (with impact), completed mandatory checks, and unexecuted/unavailable optional checks.
- Strict State A guard: Never emit custom `✅` headers (e.g., `✅ TSAR v1.2.0 — Adoption Successful`) and never emit State A (`✅`) when any capability or optional check is `unsupported`, `unavailable`, or `unexecuted` — use State C (`⚠️`) or State B (`❌`).
- Verification integrity & persistence rule: Source consultation does not guarantee policy conformance or prove behavioral security effectiveness — never claim it does. Report same-session memory writes as `completed (unverified across fresh session)` until verified in a fresh session.

**End of Protocol.**
```

The prompt is an onboarding request, not an installation mechanism by itself. The agent still needs the relevant GitHub, shell, filesystem, and configuration capabilities, plus user permission for actions that modify the environment.

For the complete procedure and platform-specific limitations, see [Universal Agent Onboarding](docs/universal-agent-onboarding.md).

## Installation

For compatible coding agents with shell access, install all valid TSAR skills globally across detected agents:

```bash
npx skills add mohamedelghazali/TSAR -g --all
```

Verify the installation:

```bash
npx skills ls -g
```

Check for and apply updates:

```bash
npx skills check
npx skills update -g
```

**Installation boundaries:** the command installs skills only for agents supported by the Skills CLI and detected in the environment. It does not guarantee that every agent loads TSAR on every turn. A model with GitHub browsing but no shell access may be able to read and apply the rules in the current session, but cannot perform a local installation. See [persistence boundaries](docs/universal-agent-onboarding.md#persistence-boundaries).

## Deployment Modes

### 1. Local installation

Install TSAR skills and use the repository's CLI, scanners, hooks, and verification scripts in your development environment. This is the appropriate route when you want local tooling to inspect files.

### 2. Direct agent adoption

Provide the repository URL and the [adoption prompt](#adopt-tsar-in-your-ai-agent) to an agent that has GitHub access. The agent can inspect the directives and relevant rules, then configure supported project or persistent instructions when its platform permits.

### 3. Combined deployment

Use agent instructions to guide secure implementation, and use local scanners, tests, hooks, and CI for independent checks. This provides stronger coverage than relying on prompts alone.

## Supported AI Agents

TSAR currently provides dedicated prompt or instruction integrations for:

- Claude and Claude Code
- GPT / ChatGPT
- DeepSeek-Coder
- Qwen-Coder
- Gemini
- Llama
- Cursor
- GitHub Copilot
- Manus
- Windsurf
- SuperNinja
- Replit Agent
- Devin
- Kimi

**Compatibility note:** support means TSAR provides an shared universal instruction source and a compatibility profile or documented fallback; it does not mean every product supports global skill installation. Available capabilities vary by product, plan, runtime, and permissions. Check the [Agent Compatibility Matrix](docs/agent-compatibility-matrix.md) before choosing an installation method.

## Quick Start: Local Project Setup

Clone TSAR:

```bash
git clone https://github.com/mohamedelghazali/TSAR.git
cd TSAR
```

Initialize TSAR in an existing project directory:

```bash
python ./tools/tsar-cli/tsar.py init /path/to/project
```

Run the available scanners against that project:

```bash
python ./tools/tsar-cli/tsar.py scan /path/to/project
```

Run the orchestrator:

```bash
python ./tools/tsar-orchestrator/orchestrator.py /path/to/project
```

Replace `/path/to/project` with the path to your actual project directory. Review the CLI output and generated files before treating initialization or scanning as complete.

## Local Development and Pre-Push Verification

Install the declared development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Inspect the working tree:

```bash
git status
git diff --check
git diff
```

On Linux, macOS, Git Bash, or WSL, run the full verification script:

```bash
bash ./verify-all.sh
```

On Windows PowerShell, run the core checks individually:

```powershell
python -m pip install -r requirements-dev.txt
python scripts/lint_rules.py
python scripts/check-no-empty-files.py
python skills/secret-scanner/scanner.py .
python skills/secure-review/review.py examples/secure
python skills/crypto-inventory/inventory.py examples/secure
python -m pytest tests/ -q
git diff --check
```

The full verification script also checks manifest integrity, anti-pattern detection, compliance references, orchestration, reporting, and optional OPA, LSP, and Terraform integrations. Optional checks may be skipped when their tools are unavailable; a skipped check is not a pass.

Do not proceed while a required check is failing. Fix the underlying issue, rerun the relevant check, and then rerun the full suite.

**Verification principle:** local checks are a prerequisite, not a replacement for CI or human review. Never report a check as passed unless its result was observed.

## Coverage

The repository currently documents:

- **175 active governance files (171 domain security rule files + 4 core directives)** across **37 rule domains** (the `rules/blockchain/README.md` overview is not counted as an active rule).
- **15 AI-agent instruction integrations**, plus a universal fallback.
- **9 programming languages** represented in secure reference examples.
- **5 compliance frameworks** mapped: SOC 2, ISO 27001, PCI DSS, HIPAA, and GDPR.
- CLI, orchestrator, reporting, LSP, dashboard, and CI/CD integrations.

See [Release Qualification](docs/release-qualification.md) for release evidence and qualification status.

## Enforcement Model and Limitations

TSAR combines three practical enforcement points:

1. **Generation-time guidance:** instruction files communicate relevant TSAR requirements to supported agents.
2. **Local verification:** scanners and project hooks inspect selected code patterns and can return findings or non-zero exit codes.
3. **CI governance:** repository workflows validate configured rules, policies, examples, and project changes. Merge blocking requires the repository to configure required status checks.

These mechanisms have different guarantees. Prompt instructions can be ignored or incompletely followed. Static scanners can produce false positives and false negatives. CI can validate only the checks actually configured and executed. Runtime protections must be implemented in the application or infrastructure.

TSAR therefore reduces risk and improves consistency; it does not guarantee vulnerability-free code, certify compliance, or replace threat modeling, penetration testing, independent security review, and operational monitoring.

## Repository Structure

| Directory | Purpose |
|---|---|
| `system/` | Core directives, prohibitions, enforcement levels, lifecycle |
| `rules/` | Domain-specific security requirements |
| `skills/` | Agent Skills packages and security helper tools |
| `tools/` | CLI, orchestrator, reports, LSP, dashboard |
| `integrations/` | CI/CD templates and Git hooks |
| `prompts/` | One canonical universal instruction set plus backward-compatible migration pointers |
| `examples/` | Secure and anti-pattern code examples |
| `docs/` | Architecture, onboarding, compliance mappings, and guides |
| `policies/` | Policy-as-code examples, including OPA and Cedar policies |
| `tests/` | Automated test suite |

## Design Principles

1. **Fail closed where configured** — critical workflows should not silently proceed when required rules are unavailable.
2. **Structural separation** — keep core policy, domain rules, agent instructions, and verification tools distinct.
3. **Defense in depth** — combine guidance with scanners, hooks, CI, and human review.
4. **Time-bound exceptions** — document suppressions and define an expiry.
5. **Evidence-driven** — retain reviewable test results, CI logs, and reports.
6. **Portable** — support multiple agents and development environments.
7. **Testable** — validate rules, manifests, tools, and integrations continuously.

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [Universal Agent Onboarding](docs/universal-agent-onboarding.md)
- [Agent Skills](docs/agent-skills.md)
- [Agent Integration](docs/agent-integration.md)
- [Agent Compatibility Matrix](docs/agent-compatibility-matrix.md)
- [Compliance Mappings](docs/compliance/README.md)
- [Roadmap](ROADMAP.md)
- [Final Review](docs/final-review.md)
- [Release Qualification](docs/release-qualification.md)

## License

TSAR is licensed under the **MIT License**, an OSI-approved Open Source license. See [LICENSE](LICENSE) for the full terms and copyright holder details.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.
