# Agent Compatibility Matrix

TSAR ships 15 agent-specific instruction files and one universal fallback. These are prompt/configuration integrations; they are not privileged native security hooks inside the AI providers.

| Agent | Prompt File | Setup / Fetch Method | Local Fallback | Integration Type |
|---|---|---|---|---|
| Claude (chat) | prompts/claude.md | network | paste rules | system instructions |
| Claude Code | prompts/claude-code.md | network | CLAUDE.md | project instructions |
| GPT | prompts/gpt.md | network | paste rules | system instructions |
| DeepSeek-Coder | prompts/deepseek-coder.md | network | paste rules | system instructions |
| Qwen-Coder | prompts/qwen-coder.md | network | paste rules | system instructions |
| Gemini | prompts/gemini.md | network | paste rules | system instructions |
| Llama | prompts/llama.md | network | paste rules | system instructions |
| Cursor | prompts/cursor.md | network | .cursorrules | project instructions |
| GitHub Copilot | prompts/github-copilot.md | network | copilot-instructions.md | repository instructions |
| Manus | prompts/manus.md | network | paste rules | agent instructions |
| Windsurf | prompts/windsurf.md | network | .windsurfrules | project instructions |
| SuperNinja | prompts/superninja.md | network | paste rules | agent instructions |
| Replit Agent | prompts/replit-agent.md | network | paste rules | agent instructions |
| Devin | prompts/devin.md | network | paste rules | agent instructions |
| Kimi | prompts/kimi.md | network | paste rules | system instructions |

## What "Supported" Means

- A dedicated TSAR instruction file exists for each listed agent.
- The integration requires the user/team to install or paste the instructions using the configuration mechanism available in that product.
- Provider behavior and configuration semantics can change. Verify the relevant product's current documentation before deploying an integration.
- Prompt instructions influence model behavior but cannot guarantee that an agent will obey every rule or prevent every unsafe output.
- Use TSAR scanners, local hooks, and CI checks for deterministic checks on detectable patterns. Keep human security review for design and logic flaws.

## Local Fallback Procedure

1. Clone TSAR to .tsar/ in the project.
2. Update the project instructions to read from .tsar/manifest.yaml.
3. Commit .tsar/ (excluding its nested .git directory).
4. Set TSAR_DIR=.tsar in CI.

## Verification

After integration, ask the agent to generate a query function:
- Correct: parameterized query.
- Incorrect: string concatenation.

This is a smoke test for instruction loading, not proof of complete security coverage. Also run the project scanner and CI checks.
