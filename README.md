# 🛡️ TSAR — The Ultimate Security Governance Layer for AI Coding Agents

> **Stop vulnerabilities at the source. Secure every line of AI-generated code.**

TSAR is an AI security governance layer for AI-assisted software development. It provides **171 active security rule files across 37 domains**, covering **Cryptography, Cloud Security, OWASP, and more**, together with dedicated instruction packs for **15 AI coding agents**.

Built for security-conscious engineering teams, TSAR brings security policy closer to the point where code is generated—then reinforces it with local scanners, repository hooks, CI checks, and policy validation.

**Security-first AI development. Governed at the source.**

**Repository version:** 1.1.1 (see VERSION, manifest.yaml, and tools/tsar-cli/pyproject.toml). The v2.0 roadmap is proposed work, not the current release. See [Release Qualification](docs/release-qualification.md) for current evidence and release status.

## Install

If an AI agent is given this repository link and asked to adopt TSAR, it should follow [Universal Agent Onboarding](docs/universal-agent-onboarding.md), inspect its environment, install the compatible TSAR skills, configure supported durable instructions when permitted, and verify what it actually changed.

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

**Important:** the URL is a discovery and onboarding entry point, not executable code. A model can perform installation only if its environment provides shell/tool access and the necessary permissions. Global skill installation does not force every model to load TSAR on every turn, nor does it modify model training or provider-level system prompts. See [persistence boundaries](docs/universal-agent-onboarding.md#persistence-boundaries).

## How to Adopt TSAR in Your AI Agent

Use this short bootstrap prompt in your AI agent's chat, project instructions, or supported global-instructions setting:

```text
Adopt TSAR as your security-governance framework for all relevant software engineering, coding, architecture, infrastructure, and cybersecurity tasks.

Official repository: https://github.com/mohamedelghazali/TSAR

1. Read AGENTS.md, manifest.yaml, and docs/universal-agent-onboarding.md.
2. Review the core directives: system/CORE_DIRECTIVE.md, system/DO_NOT_GENERATE.md, system/ENFORCEMENT_LEVELS.md, and system/LIFECYCLE.md.
3. If shell access and permission are available, install compatible skills with:
   npx skills add mohamedelghazali/TSAR -g --all
4. Configure supported persistent agent or project instructions using prompts/global-bootstrap.md. Preserve existing user settings.
5. Verify what was installed, configured, and loaded. Report unsupported agents and incomplete steps.
6. Apply relevant TSAR rules and skills proactively; scan, review, and verify engineering changes before delivery.
7. Check the upstream version and update installed skills when appropriate.

Operating cycle:
CONSULT → CLASSIFY → DESIGN → IMPLEMENT → SCAN → REVIEW → VERIFY → REPORT

Treat TSAR as the standing security reference within your actual platform permissions. Never claim installation, persistence, enforcement, or verification unless performed and confirmed. If installation is unavailable, apply relevant directives in the current session and state the limitation.
```

The prompt requests adoption; it does not itself install software or override provider system instructions. For the complete procedure, see [Universal Agent Onboarding](docs/universal-agent-onboarding.md).

## Deployment Modes: Local or Agent-Based

TSAR can be adopted in two complementary ways:

### 1. Local Installation on Your Device

Install TSAR skills and tools in your local development environment. Compatible agents can discover and use the installed skills across supported projects. You can also run TSAR scanners, CLI tools, hooks, and verification scripts directly on your machine.

```bash
npx skills add mohamedelghazali/TSAR -g --all
npx skills ls -g
```

### 2. Direct Adoption by Your AI Agent

Give your agent the TSAR repository URL and the [adoption prompt above](#how-to-adopt-tsar-in-your-ai-agent). The agent reads the governance directives and applicable rules, then configures supported project or persistent instructions and verifies its actual capabilities.

This mode can work without a local global installation when the agent can access repository files. Persistent adoption depends on the agent platform's supported configuration features. A chat-only agent without shell or configuration access can apply the relevant rules in the current session, but cannot install local skills or guarantee persistence across future sessions.

These modes can be combined: use agent instructions for secure generation and local scanners/CI for independent verification.

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

**Compatibility note:** support means TSAR provides an agent-specific prompt/instruction path or documented fallback; it does not mean every product supports global skill installation. Available capabilities vary by product, plan, runtime, and permissions. Check the [Agent Compatibility Matrix](docs/agent-compatibility-matrix.md) before choosing an installation method.

## Local Development and Pre-Push Verification

Run security and quality checks locally before committing and pushing changes.

### 1. Prepare the environment

Install the declared development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

### 2. Inspect the working tree

```bash
git status
git diff --check
git diff
```

### 3. Run the full verification suite

From Linux, macOS, Git Bash, or WSL:

```bash
bash ./verify-all.sh
```

On Windows PowerShell, run the following core checks individually (the full script requires a Bash-compatible environment):

```powershell
py -3 -m pip install -r requirements-dev.txt
py -3 scripts/lint_rules.py
py -3 scripts/check-no-empty-files.py
py -3 skills/secret-scanner/scanner.py .
py -3 skills/secure-review/review.py examples/secure
py -3 skills/crypto-inventory/inventory.py examples/secure
py -3 -m pytest tests/ -q
git diff --check
```

The full verification script also checks manifest integrity, anti-pattern detection, compliance references, orchestration, reporting, and optional OPA, LSP, and Terraform integrations. Optional checks may be skipped when their tools are unavailable; a skipped check is not a pass.

### 4. Fix findings and repeat

Do not proceed while a required check is failing. Fix the underlying issue and rerun the relevant check, then rerun the full suite.

### 5. Review and push

```bash
git status --short
git diff --stat
git diff
git add .
git commit -m "Describe the verified change"
git push origin HEAD
```

Open a Pull Request and wait for independent CI validation and review before merging.

**Pre-push principle:** local verification is a prerequisite, not a replacement for CI or human review. Never report a check as passed unless its result was observed.

## Coverage

- **171 active rule files** across **37 rule domains** (rules/blockchain/README.md is an overview file, not a rule).
- **15 AI agents** with dedicated prompt/instruction files, plus one universal fallback.
- **9 programming languages** represented in secure reference examples.
- **5 compliance frameworks** mapped (SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR).
- CLI, orchestrator, reporting, LSP, dashboard, and CI/CD integrations.

## How Governance Is Enforced

TSAR uses multiple enforcement layers:

1. **Generation-time guidance:** agent-specific instruction files communicate the applicable TSAR rules to supported agents.
2. **Local verification:** scanners and project hooks inspect code and can block detected high-risk patterns.
3. **CI governance:** repository workflows validate rules, policies, examples, and project changes before merge.

**Important limitation:** prompt files are instruction-level integrations, not privileged native controls inside each AI provider. An agent may ignore or incompletely follow instructions. Actual enforcement depends on installing the relevant prompt/configuration and running the scanners and CI gates. TSAR does not guarantee vulnerability-free code or replace independent security review.

## Quick Start

    git clone https://github.com/mohamedelghazali/TSAR.git
    cd TSAR
    ./tools/tsar-cli/tsar.py init /path/to/project --agent cursor
    ./tools/tsar-cli/tsar.py scan /path/to/project
    ./tools/tsar-orchestrator/orchestrator.py /path/to/project

## Structure

| Directory | Purpose |
|---|---|
| system/ | Core directive, prohibitions, enforcement levels |
| rules/ | 37 domains of security rules |
| skills/ | Scanners and security helpers, plus Agent Skills packages |
| tools/ | CLI, orchestrator, report, LSP, dashboard |
| integrations/ | CI/CD templates and hooks |
| prompts/ | Agent-specific and universal instruction files |
| examples/ | Secure and anti-pattern code |
| docs/ | Guides, compliance mappings, architecture |
| policies/ | OPA/Cedar policies |
| tests/ | Automated test suite |

## Verification

Run ./verify-all.sh to execute the repository verification suite, including rule linting, manifest integrity, empty-file detection, security scanners, compliance references, tests, orchestration, reporting, and available OPA/LSP/Terraform checks.

## Design Principles

1. **Fail closed** — refuse Tier-1 work when required rules cannot be loaded.
2. **Structural over semantic** — keep policy, rules, and agent prompts distinct.
3. **Defense in depth** — combine generation guidance with scanners and CI.
4. **Time-bound exceptions** — every suppression should have an expiry.
5. **Evidence-driven** — produce reviewable verification artifacts.
6. **Portable** — avoid unnecessary vendor lock-in.
7. **Testable** — validate rules and integrations continuously.

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

TSAR uses a custom source-available license. Defined non-commercial uses are permitted; commercial use requires prior written authorization and a separate commercial license. This is not an OSI-approved Open Source license. See [LICENSE](LICENSE) for the full terms and the treatment of previously distributed MIT versions.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.
