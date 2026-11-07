# Agent Compatibility Matrix

TSAR ships 15 agent-specific instruction files and one universal fallback. The 15 entries below describe instruction/configuration integrations, not 15 independently verified native runtime enforcement adapters.

| Agent | Prompt File | Setup / Fetch Method | Local Fallback | Integration Type | Assurance / CI Evidence |
|---|---|---|---|---|---|
| Claude (chat) | prompts/claude.md | network | paste rules | system instructions | E0/E1 instruction-level; inventory validation only |
| Claude Code | prompts/claude-code.md | network | CLAUDE.md | project instructions + optional native TSAR hooks (strict file-tool profile; see docs/claude-code-enforcement.md) | E0/E1 instructions; separate hook conformance tests, not live authenticated-provider proof |
| GPT | prompts/gpt.md | network | paste rules | system instructions | E0/E1 instruction-level; inventory validation only |
| DeepSeek-Coder | prompts/deepseek-coder.md | network | paste rules | system instructions | E0/E1 instruction-level; inventory validation only |
| Qwen-Coder | prompts/qwen-coder.md | network | paste rules | system instructions | E0/E1 instruction-level; inventory validation only |
| Gemini | prompts/gemini.md | network | paste rules | system instructions | E0/E1 instruction-level; inventory validation only |
| Llama | prompts/llama.md | network | paste rules | system instructions | E0/E1 instruction-level; inventory validation only |
| Cursor | prompts/cursor.md | network | .cursorrules | project instructions | E0/E1 instruction-level; inventory validation only |
| GitHub Copilot | prompts/github-copilot.md | network | copilot-instructions.md | repository instructions | E0/E1 instruction-level; inventory validation only |
| Manus | prompts/manus.md | network | paste rules | agent instructions | E0/E1 instruction-level; inventory validation only |
| Windsurf | prompts/windsurf.md | network | .windsurfrules | project instructions | E0/E1 instruction-level; inventory validation only |
| SuperNinja | prompts/superninja.md | network | paste rules | agent instructions | E0/E1 instruction-level; inventory validation only |
| Replit Agent | prompts/replit-agent.md | network | paste rules | agent instructions | E0/E1 instruction-level; inventory validation only |
| Devin | prompts/devin.md | network | paste rules | agent instructions | E0/E1 instruction-level; inventory validation only |
| Kimi | prompts/kimi.md | network | paste rules | system instructions | E0/E1 instruction-level; inventory validation only |

## What "Supported" Means

- A dedicated TSAR instruction file exists for each listed agent.
- The integration requires the user/team to install or paste the instructions using the configuration mechanism available in that product.
- The `Agent Compatibility Inventory` CI job verifies that all 15 matrix entries map to existing, unique prompt files and that the matrix does not imply provider-native enforcement for all agents.
- This inventory check proves repository consistency only. It does not call any provider, verify current provider APIs, prove that an agent loaded the prompt, or demonstrate that the model follows TSAR.
- Provider behavior and configuration semantics can change. Verify the relevant product's current documentation before deploying an integration.
- Prompt instructions influence model behavior but cannot guarantee that an agent will obey every rule or prevent every unsafe output.
- Use TSAR scanners, local hooks, policy gates, CI checks, and human security review for deterministic checks on detectable patterns and design/logic flaws.

## Assurance Levels and What Is Actually Tested

- **E0/E1 — instruction-level integration:** a prompt, project instruction, system instruction, or repository instruction is available/configured. This is the current documented level for the 15 listed prompt integrations.
- **Claude Code hook profile:** an additional product-specific integration exists and has dedicated unit and Windows process/contract tests. Those tests establish the configured hook behavior and fail-closed protocol on the tested path; they do not establish authenticated live-provider conformance or universal Claude enforcement.
- **Shared TSAR core tests:** validate policy parsing, scanners, CLI, lifecycle, tool-boundary building blocks, and repository gates. Passing these tests does not mean all 15 providers were launched or tested.
- **Live provider conformance:** must be performed separately for each provider/runtime using an authenticated, supported environment. Record product/runtime version, integration mode, test evidence, limitations, and the highest enforcement level actually demonstrated. Do not infer live conformance from prompt-file existence or shared core tests.

## Local Fallback Procedure

1. Clone TSAR to .tsar/ in the project.
2. Update the project instructions to read from .tsar/manifest.yaml.
3. Commit .tsar/ (excluding its nested .git directory).
4. Set TSAR_DIR=.tsar in CI.

## Verification

After integration, ask the agent to generate a query function:
- Correct: parameterized query.
- Incorrect: string concatenation.

This is a smoke test for instruction loading, not proof of complete security coverage. Also run the project scanner and CI checks. For a provider-specific runtime claim, use the live conformance process described above.

## Native hook integrations

Claude Code currently has the documented optional TSAR hook integration that can block prompts and tool calls through its configured native lifecycle hooks. This is a product-specific implementation, not a shared hook implementation for the other 14 entries. It remains limited to the exact hook events and tools configured in the strict profile; it is not proof of provider-wide or operating-system-level enforcement. See [Claude Code enforcement integration](claude-code-enforcement.md).
