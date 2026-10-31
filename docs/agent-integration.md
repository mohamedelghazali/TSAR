# Agent Integration Guide

TSAR provides 15 agent-specific instruction files. Install the matching file using the project or system-instruction mechanism supported by your agent.

## Claude Code
1. Copy prompts/claude-code.md to CLAUDE.md.
2. Commit it to the repository root.
3. Confirm that Claude Code loads the project instructions for the session.

## GitHub Copilot
1. Create .github/copilot-instructions.md.
2. Paste the contents of prompts/github-copilot.md.
3. Keep TSAR scanners and CI checks enabled; suggestions still require review.

## Cursor
1. Create the project instruction file supported by your installed Cursor version (historically .cursorrules; check current Cursor documentation).
2. Paste the contents of prompts/cursor.md.
3. Confirm that project rules are enabled for the workspace.

## Windsurf
1. Create the project rules file supported by your installed Windsurf version.
2. Paste the contents of prompts/windsurf.md.
3. Confirm that the rules are active for the workspace.

## Devin / Replit Agent / Manus / SuperNinja
1. Add the matching prompt to the agent's instructions or context field.
2. Ensure network access to raw.githubusercontent.com if using remote rules.
3. If network access is unavailable, vendor the manifest and active files locally under .tsar/.

## GPT / Gemini / Llama / Kimi / DeepSeek / Qwen
1. Paste the matching prompt into the system or project instructions supported by the product.
2. Include the manifest URL if the environment permits retrieval.
3. For local models, pre-download the rules and include relevant content in the context window.

## Enforcement Model and Limitations

These integrations load instructions; they do not install privileged controls inside the model provider. Prompt compliance is not guaranteed. For reliable repository-level enforcement:

- Run TSAR scanners against generated and modified code.
- Install the appropriate pre-commit or repository hooks.
- Run the TSAR CI integration on every pull request.
- Require security review for high-impact changes and design-level risks.

A prompt-only integration must never be represented as a guarantee that unsafe code cannot be generated.
