# Agent Compatibility Matrix

TSAR maintains **one authoritative instruction set** and a registry of 15 compatibility profiles. The profiles describe how each product can receive the same policy text; they are not independent policy copies or proof of provider enforcement.

Canonical policy source: [prompts/universal.md](../prompts/universal.md)  
Machine-readable profile registry: [integrations/agent-profiles.json](../integrations/agent-profiles.json)

| Agent | Instruction Source | Profile Key | Delivery | Platform Target | Native Adapter | Assurance Baseline |
|---|---|---|---|---|---|---|
| Claude (chat) | prompts/universal.md | claude | system_instructions | Provider system-instructions field | — | E0/E1 |
| Claude Code | prompts/universal.md | claude-code | project_instructions | CLAUDE.md / project instructions | integrations/claude-code/settings.json | E0/E1 + separately tested hook path |
| GPT | prompts/universal.md | gpt | system_instructions | Provider system-instructions field | — | E0/E1 |
| DeepSeek-Coder | prompts/universal.md | deepseek-coder | system_instructions | Provider system-instructions field | — | E0/E1 |
| Qwen-Coder | prompts/universal.md | qwen-coder | system_instructions | Provider system-instructions field | — | E0/E1 |
| Gemini | prompts/universal.md | gemini | system_instructions | Provider system-instructions field | — | E0/E1 |
| Llama | prompts/universal.md | llama | system_instructions | Selected local/hosted runtime instruction mechanism | — | E0/E1 |
| Cursor | prompts/universal.md | cursor | project_instructions | Cursor workspace/project rules (version-dependent) | — | E0/E1 |
| GitHub Copilot | prompts/universal.md | github-copilot | repository_instructions | .github/copilot-instructions.md | — | E0/E1 |
| Manus | prompts/universal.md | manus | agent_instructions | Manus agent instructions/context | — | E0/E1 |
| Windsurf | prompts/universal.md | windsurf | project_instructions | Windsurf workspace/project rules | — | E0/E1 |
| SuperNinja | prompts/universal.md | superninja | agent_instructions | SuperNinja agent instructions/context | — | E0/E1 |
| Replit Agent | prompts/universal.md | replit-agent | project_instructions | Replit project instructions/context | — | E0/E1 |
| Devin | prompts/universal.md | devin | agent_instructions | Devin agent instructions/context | — | E0/E1 |
| Kimi | prompts/universal.md | kimi | system_instructions | Provider system-instructions field | — | E0/E1 |

## Architecture and compatibility contract

- **Single source of truth:** all 15 profiles resolve to exactly prompts/universal.md. Security policy text must not be copied into provider-specific files.
- **Compatibility profiles:** integrations/agent-profiles.json records the delivery mechanism, supported configuration target, and optional native adapter. Update this registry when platform setup changes.
- **Legacy paths:** prompts/<agent>.md files are short migration pointers retained for old links. They are not independent prompts and must not accumulate policy content.
- **Native adapters:** add a platform-specific adapter only when the platform exposes a supported integration surface and the adapter has dedicated tests. Claude Code's hook configuration remains a specialized path; it is not shared or implied for the other 14 profiles.
- **No invented enforcement:** an instruction file can influence model behavior but cannot guarantee compliance or block tool execution. A prompt-only profile remains E0/E1 until stronger controls are demonstrated.
- **Inventory CI:** validates the 15 unique profile records, common policy source, compatibility pointers, matrix alignment, and the narrowly scoped Claude Code adapter reference. It does not call providers or establish live runtime conformance.
- **Live provider conformance:** must be separately run against an authenticated, supported product/runtime. Record version, integration mechanism, test results, limitations, and the highest E-level actually demonstrated.

## Local fallback procedure

1. Clone TSAR into the project (for example, .tsar/).
2. Configure the agent's supported instruction mechanism to load .tsar/prompts/universal.md.
3. Use the matching profile in .tsar/integrations/agent-profiles.json to determine the host-specific target.
4. Set TSAR_DIR=.tsar in CI where applicable.
5. Keep policy files pinned to one immutable TSAR commit and verify the manifest before security-sensitive work.

## Verification

After loading the shared instructions, use a harmless smoke test such as requesting a parameterized database query and verify that the response uses parameter binding rather than string concatenation. This checks instruction loading only. Also run deterministic TSAR scanners and CI checks. For provider-specific runtime claims, follow the [15-Agent Runtime Conformance Plan](agent-runtime-conformance-plan.md).

## Native hook integrations

Claude Code currently has the documented optional TSAR hook integration. Its guarantees apply only to the exact hook events, tools, and strict profile covered by its tests. It does not establish authenticated live-provider conformance or generalize to other providers. See [Claude Code enforcement integration](claude-code-enforcement.md).
