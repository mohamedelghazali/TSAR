# Getting Started with TSAR

## 1. Choose Your Agent

Select the exact TSAR instruction file for the agent or model you use. Every supported entry below has its own file in `prompts/`; do not use a generic placeholder such as "corresponding file".

| Agent / model | File to copy | Where to place or paste it |
|---|---|---|
| Claude (chat) | [`prompts/claude.md`](../prompts/claude.md) | Paste into the system instructions or project instructions available in your Claude workspace. |
| Claude Code | [`prompts/claude-code.md`](../prompts/claude-code.md) | Copy to `CLAUDE.md` in the project root. |
| GPT / ChatGPT | [`prompts/gpt.md`](../prompts/gpt.md) | Paste into the system instructions, a custom GPT's instructions, or project instructions supported by your ChatGPT environment. |
| DeepSeek-Coder | [`prompts/deepseek-coder.md`](../prompts/deepseek-coder.md) | Paste into the model's system prompt or the coding environment's project instructions. |
| Qwen-Coder | [`prompts/qwen-coder.md`](../prompts/qwen-coder.md) | Paste into the model's system prompt or the coding environment's project instructions. |
| Gemini | [`prompts/gemini.md`](../prompts/gemini.md) | Paste into the system instructions or project instructions available in your Gemini environment. |
| Llama | [`prompts/llama.md`](../prompts/llama.md) | Use as the system prompt when launching the model, or add it to the local inference application's model/session instructions. |
| Cursor | [`prompts/cursor.md`](../prompts/cursor.md) | Add the contents as a project rule using the rules mechanism supported by your Cursor version (the legacy filename is `.cursorrules`). |
| GitHub Copilot | [`prompts/github-copilot.md`](../prompts/github-copilot.md) | Copy the contents to `.github/copilot-instructions.md` in the repository. |
| Manus | [`prompts/manus.md`](../prompts/manus.md) | Paste into the agent's project instructions or persistent agent instructions. |
| Windsurf | [`prompts/windsurf.md`](../prompts/windsurf.md) | Add the contents as workspace/project rules using the mechanism supported by your Windsurf version (legacy filename: `.windsurfrules`). |
| SuperNinja | [`prompts/superninja.md`](../prompts/superninja.md) | Paste into the agent's instructions or project context. |
| Replit Agent | [`prompts/replit-agent.md`](../prompts/replit-agent.md) | Add to the Replit project's agent instructions or context. |
| Devin | [`prompts/devin.md`](../prompts/devin.md) | Add to the Devin project's instructions or knowledge/context configuration. |
| Kimi | [`prompts/kimi.md`](../prompts/kimi.md) | Paste into the model's system prompt or the coding environment's project instructions. |

**Copying instructions:** open the linked Markdown file, copy its complete contents, and paste them into the destination supported by your product. For file-based destinations, create the destination file and preserve the Markdown content. Product interfaces and supported configuration locations can change, so use the current product documentation if a destination has moved.

**Important:** these files provide agent-specific instructions; they do not install privileged controls inside a model or guarantee that the model will follow every rule. For stronger verification, combine them with TSAR's scanners, hooks, tests, and CI checks.

For the complete support scope and limitations, see the [Agent Compatibility Matrix](agent-compatibility-matrix.md) and [Agent Integration Guide](agent-integration.md).

## 2. Enable Manifest Fetching

The prompt file instructs the agent to fetch `manifest.yaml` from GitHub at session start. If your agent cannot reach the internet, copy `manifest.yaml` and all `active_files` into your project under `.tsar/` and update the prompt to read from there.

## 3. Add Pre-Commit Hooks (Optional)

```bash
cp integrations/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## 4. Add CI Enforcement

Copy the appropriate integration from `integrations/` into your repository:

- GitHub Actions: `integrations/github-actions/tsar.yml`
- GitLab CI: `integrations/gitlab-ci/tsar.yml`
- Bitbucket Pipelines: `integrations/bitbucket/tsar.yml`
- Azure DevOps: `integrations/azure-devops/tsar.yml`

## 5. Verify

Run the scanners locally:

```bash
python skills/secret-scanner/scanner.py .
python skills/secure-review/review.py .
python skills/crypto-inventory/inventory.py .
```

## 6. Update Rules

The manifest version changes when upstream standards update. The agent reloads automatically on version mismatch. To update manually:

```bash
git pull
python scripts/lint_rules.py
```
