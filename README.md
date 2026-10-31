# TSAR — Security Governance Layer for AI-Generated Code

TSAR is an enforceable security policy repository injected into AI coding agents.
It provides mandatory rules, platform baselines, cryptographic standards, and
agentic-AI controls, with upstream fingerprint monitoring and manual rule review before updates.

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

## License

The current repository license is [MIT](LICENSE). A proposed future licensing transition is documented in [licensing-transition.md](docs/licensing-transition.md); it does not change existing MIT grants.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.
