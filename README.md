# 🛡️ TSAR — The Ultimate Security Governance Layer for AI Coding Agents

> **Stop vulnerabilities at the source. Secure every line of AI-generated code.**

TSAR is an AI security governance layer designed to help prevent vulnerabilities before they enter your codebase. It enforces **170+ strict security rules** spanning **Cryptography, Cloud Security, and OWASP** across Claude, Gemini, GPT-4, Kimi, Cursor, GitHub Copilot, and **15+ AI coding agents**.

Built for security-conscious AI-assisted development, TSAR brings security policy closer to the point where code is generated—so teams can govern how AI coding agents produce and modify software, rather than relying only on downstream detection.

**Security-first AI development. Governed at the source.**

**Repository version:** 1.1.1 (see `VERSION`, `manifest.yaml`, and
`tools/tsar-cli/pyproject.toml`). The v2.0 roadmap is proposed work, not the
current release. See [Release Qualification](docs/release-qualification.md)
for verified evidence and outstanding release gates.

## Coverage

- **37 rule domains** across application, infrastructure, cloud, data, cryptography, networking, compliance, and emerging technology.
- **15 AI agents** supported with dedicated prompts.
- **9 programming languages** with secure reference implementations.
- **5 compliance frameworks** mapped (SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR).
- **6 tools**: CLI, orchestrator, report, LSP, dashboard, and CI integrations.

## Quick Start

```bash
git clone https://github.com/mohamedelghazali/TSAR.git
cd TSAR

# Bootstrap into your project
./tools/tsar-cli/tsar.py init /path/to/project --agent cursor

# Or run all checks on any project
./tools/tsar-cli/tsar.py scan /path/to/project
./tools/tsar-orchestrator/orchestrator.py /path/to/project
```

## Supported Agents

Claude, Claude Code, GPT, DeepSeek-Coder, Qwen-Coder, Gemini, Llama, Cursor,
GitHub Copilot, Manus, Windsurf, SuperNinja, Replit Agent, Devin, Kimi.

## Structure

| Directory | Purpose |
|---|---|
| `system/` | Core directive, prohibitions, enforcement levels |
| `rules/` | 37 domains of security rules |
| `skills/` | Runnable scanners and helpers |
| `tools/` | CLI, orchestrator, report, LSP, dashboard |
| `integrations/` | CI/CD templates for 4 platforms |
| `prompts/` | Agent-specific instruction files |
| `examples/` | Secure and anti-pattern code |
| `docs/` | Guides, compliance mappings, architecture |
| `policies/` | OPA/Cedar policies |
| `tests/` | Full pytest suite |

## Verification

```bash
./verify-all.sh
```

This runs every check: lint, manifest integrity, empty file detection,
secret scanners, secure review, crypto inventory, compliance references,
full test suite, orchestrator, report generation, and optional
OPA/LSP/Terraform builds.

## Design Principles

1. **Fail closed** — refuse Tier-1 work when rules cannot be loaded.
2. **Structural over semantic** — prompts separated by role.
3. **Defense in depth** — no single point of failure.
4. **Time-bound exceptions** — every suppression has an expiry.
5. **Evidence-driven** — every control produces audit evidence.
6. **Portable** — no vendor lock-in.
7. **Testable** — every rule has a test.

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [Agent Integration](docs/agent-integration.md)
- [Compliance Mappings](docs/compliance/README.md)
- [Roadmap](ROADMAP.md)
- [Final Review](docs/final-review.md)
- [Release Qualification](docs/release-qualification.md)

## License

TSAR uses a custom source-available license. Defined non-commercial uses are
permitted; commercial use requires prior written authorization and a separate
commercial license. This is not an OSI-approved Open Source license. See
[LICENSE](LICENSE) for the full terms and the treatment of previously
distributed MIT versions.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.
