# Agent Integration Guide

## Claude Code
1. Copy `prompts/claude-code.md` to `CLAUDE.md`.
2. Commit to repository root.
3. Claude Code reads `CLAUDE.md` at session start and follows the manifest fetch instruction.

## GitHub Copilot
1. Create `.github/copilot-instructions.md`.
2. Paste contents of `prompts/github-copilot.md`.
3. Copilot suggestions are constrained; still verify with `skills/secure-review`.

## Cursor
1. Create `.cursorrules` at project root.
2. Paste contents of `prompts/cursor.md`.
3. Cursor applies rules to inline suggestions and chat.

## Windsurf
1. Create `.windsurfrules`.
2. Paste contents of `prompts/windsurf.md`.

## Devin / Replit Agent / Manus / SuperNinja
1. Add the prompt to the agent's "instructions" or "context" field in the platform UI.
2. Ensure network access to `raw.githubusercontent.com` is allowed.
3. If blocked, vendor the manifest and active files locally under `.tsar/`.

## GPT / Gemini / Llama / Kimi / DeepSeek / Qwen
1. Paste the prompt file into the system message.
2. Include the manifest URL; the model will fetch and cache it.
3. For local models, pre-download the rules and include them in the context window.

## Verification After Integration
Ask the agent: "Write a function that queries users by ID."
- Secure response: uses parameterized query.
- Insecure response (reject): string concatenation.
If the agent produces unsafe code, re-check that the prompt file was applied and the manifest is reachable.
