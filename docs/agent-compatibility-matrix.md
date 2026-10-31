# Agent Compatibility Matrix

| Agent | Prompt File | Fetch Method | Local Fallback | Notes |
|---|---|---|---|---|
| Claude (chat) | prompts/claude.md | network | paste rules | relies on user compliance |
| Claude Code | prompts/claude-code.md | network | CLAUDE.md | reads at session start |
| GPT | prompts/gpt.md | network | paste rules | system message |
| DeepSeek-Coder | prompts/deepseek-coder.md | network | paste rules | system message |
| Qwen-Coder | prompts/qwen-coder.md | network | paste rules | system message |
| Gemini | prompts/gemini.md | network | paste rules | system message |
| Llama | prompts/llama.md | network | paste rules | system message |
| Cursor | prompts/cursor.md | network | .cursorrules | file auto-loaded |
| GitHub Copilot | prompts/github-copilot.md | network | copilot-instructions.md | file auto-loaded |
| Manus | prompts/manus.md | network | paste rules | agent config |
| Windsurf | prompts/windsurf.md | network | .windsurfrules | file auto-loaded |
| SuperNinja | prompts/superninja.md | network | paste rules | agent config |
| Replit Agent | prompts/replit-agent.md | network | paste rules | agent config |
| Devin | prompts/devin.md | network | paste rules | agent config |
| Kimi | prompts/kimi.md | network | paste rules | system message |

## Local Fallback Procedure
1. Clone TSAR to `.tsar/` in the project.
2. Update prompt file to read from `.tsar/manifest.yaml`.
3. Commit `.tsar/` (excluding `.git` inside).
4. Set `TSAR_DIR=.tsar` in CI.

## Verification
After integration, ask the agent to generate a query function:
- Correct: parameterized query.
- Incorrect: string concatenation.
If incorrect, the prompt did not load; re-check the integration.
