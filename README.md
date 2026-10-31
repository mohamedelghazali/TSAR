# TSAR — Security Governance Layer for AI-Generated Code

TSAR is an enforceable security policy repository injected into AI coding agents. It provides mandatory rules, platform baselines, cryptographic standards, and agentic-AI controls, with automatic synchronization via manifest versioning.

## Supported Agents
Claude, Claude Code, GPT, DeepSeek-Coder, Qwen-Coder, Gemini, Llama, Cursor, GitHub Copilot, Manus, Windsurf, SuperNinja, Replit Agent, Devin, Kimi.

## Quick Start
1. Copy the relevant file from `prompts/` into your agent configuration.
2. The agent fetches `manifest.yaml` at session start.
3. Unsafe patterns are refused; secure alternatives are offered.

## Structure
- `system/` — core directive, prohibitions, enforcement levels, lifecycle.
- `rules/crypto/` — algorithms, key management, AEAD, PQC, constant-time.
- `rules/owasp-llm/` — LLM Top 10 controls.
- `rules/agentic-ai/` — tool scoping and memory integrity.
- `rules/platform/` — web, iOS, Android, firmware, distributed, edge.
- `rules/hardware/` — TPM, HSM, Secure Enclave, secure boot, side channels.
- `rules/data/` — PII and logging redaction.
- `skills/` — runnable scanners, reviewers, threat modeler, crypto inventory.
- `prompts/` — per-agent instruction files (15 agents).
- `.github/workflows/` — auto-update, validation, PR enforcement.

## Usage in a Project
Place the appropriate file from `prompts/` in your project root:
- Claude Code: `CLAUDE.md`
- Cursor: `.cursorrules`
- GitHub Copilot: `.github/copilot-instructions.md`
- Windsurf: `.windsurfrules`
- Others: prepend the prompt file to the agent's system instruction.

## License
See LICENSE.
