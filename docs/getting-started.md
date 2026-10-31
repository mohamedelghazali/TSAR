# Getting Started with TSAR

## 1. Choose Your Agent

Pick the file from `prompts/` matching your AI agent.

| Agent | File to copy | Destination |
|---|---|---|
| Claude Code | `prompts/claude-code.md` | `CLAUDE.md` in project root |
| Claude (chat) | `prompts/claude.md` | System prompt / project instructions |
| Cursor | `prompts/cursor.md` | `.cursorrules` |
| GitHub Copilot | `prompts/github-copilot.md` | `.github/copilot-instructions.md` |
| Windsurf | `prompts/windsurf.md` | `.windsurfrules` |
| Devin / Replit / Manus / SuperNinja | corresponding file | Agent configuration |
| GPT / Gemini / Llama / Kimi / DeepSeek / Qwen | corresponding file | System prompt |

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
