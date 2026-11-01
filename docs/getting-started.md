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

**Copying instructions:** open the linked Markdown file, copy its complete contents, and paste them into the destination supported by your product. Do not copy only the opening section or selected bullets: each agent file contains the full TSAR governance baseline and a platform-specific execution adapter. For file-based destinations, create the destination file and preserve the complete Markdown content. Product interfaces and supported configuration locations can change, so use the current product documentation if a destination has moved.

**What the expanded agent files contain:** each of the 15 files now describes TSAR's pre-flight and manifest-freshness process, core prohibitions, cryptography and key-management requirements, secure coding and injection prevention, web/API/identity security, privacy and data protection, cloud/container/infrastructure controls, AI/LLM/agent security, the full 37-domain rule taxonomy, the three repository OPA/Rego policy examples, available TSAR skills and tools, enforcement levels, exception handling, lifecycle verification, reporting requirements, and instructions specific to the selected model or agent environment.

**Important source-of-truth rule:** the agent files explain the complete governance scope, but the detailed technical requirements remain in the current files listed by `manifest.yaml`. For each task, the agent must read the complete applicable rule files rather than treating the prompt's domain descriptions as a replacement for those rules. Do not paste all 171 active rule files into every model prompt; load the relevant authoritative files dynamically from the manifest. This keeps the agent instructions comprehensive while ensuring that rule updates are taken from the current source.

**Enforcement behavior:** the current `manifest.yaml` sets `lifecycle.fail_closed: true` and `enforcement.allow_advisory_fallback: false`. If the manifest or required policy files cannot be accessed and no trusted, valid local copy is available, agents must stop security-sensitive implementation rather than silently switching to Advisory mode. Advisory fallback is permitted only if a future trusted manifest explicitly enables it and disables fail-closed behavior.

**Important:** these files provide agent-specific instructions; they do not install privileged controls inside a model or guarantee that the model will follow every rule. They cannot override provider-level system instructions or platform permissions. For stronger verification, combine them with TSAR's scanners, hooks, tests, policy checks, and CI checks. Tool descriptions are intentionally limited to the checks implemented by the current scripts; heuristic scanners can miss issues and produce false positives.

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

The manifest version changes when the project updates its rule inventory. The agent instructions require a version and cache-freshness check and a reload of the applicable files when a mismatch is detected, provided the agent has repository access. This is an instruction, not a provider-enforced automatic update. To update manually:

```bash
git pull
python scripts/lint_rules.py
```
