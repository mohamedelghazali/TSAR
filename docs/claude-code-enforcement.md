# Claude Code Enforcement Integration

This integration uses Claude Code's native command hooks to bind TSAR policy loading and the TSAR tool boundary to one supported provider runtime.

## What it enforces

The supplied configuration is a **strict file-tool profile**:

1. **Before each user prompt reaches Claude:** `UserPromptSubmit` runs the TSAR upstream verifier, pins one immutable upstream commit, fetches the manifest and selected policies, validates their SHA-256 values, and places verified policy files in a per-user cache outside the project tree.
2. **Mandatory policy reading:** the hook injects the exact cache paths into Claude's context. `PreToolUse` blocks every non-policy tool call until Claude successfully reads every required policy file with the `Read` tool. `PostToolUse` verifies the file bytes again and records each successful policy read.
3. **Tool boundary:** after policy reading, `PreToolUse` authorizes only the registered file tools `Read`, `Glob`, `Grep`, `LS`, `Write`, `Edit`, and `NotebookEdit`. Reads require `repo:read`; writes require `repo:write`. Paths must resolve inside the project root, except exact pinned policy-cache files during the mandatory-read phase.
4. **Native permission prompts remain active:** an authorized TSAR hook returns no `allow` decision. Claude Code's own permission system still decides whether a write tool may proceed.
5. **Audit:** pre-tool allow/deny decisions and post-tool success/failure events are appended to a per-project, per-session JSONL file under the user's TSAR audit directory. Audit write failure blocks a pre-tool action.
6. **Fail-closed behavior:** upstream failure, stale/missing policy state, altered cache content, unregistered tools, path escape, missing scopes, hook errors, and hook timeouts block the prompt or tool action when the configured Claude Code version supports `onFailure: block`.

## Installation

Install the TSAR CLI package into the same Python environment used by Claude Code:

```powershell
python -m pip install -e .\tools\tsar-cli
```

Copy `integrations/claude-code/settings.json` into the target project's `.claude/settings.json`, merging it with existing settings rather than replacing unrelated project configuration.

Start Claude Code from that project. The project must be trusted so Claude Code loads its shared settings.

## Scope configuration

The example enables:

- `repo:read` for file reads and search.
- `repo:write` for file edits and writes.

Remove `repo:write` from `TSAR_CLAUDE_SCOPES` to make the profile read-only. These scopes are host-side configuration; tool arguments cannot grant themselves scopes. Claude Code's native permission prompts remain in force for write operations.

Selected policy domains are configured through `TSAR_CLAUDE_DOMAINS`. The default profile is `development,agentic_ai,ai_security,secrets`, in addition to the four mandatory core policy files.

## Deliberate restrictions

This first integration intentionally blocks tools that are not in the strict profile, including:

- `Bash` and `PowerShell`
- `Agent` and other subagent orchestration tools
- `WebFetch` and `WebSearch`
- MCP tools, including third-party server tools
- Any unknown or newly introduced Claude Code tool

This restriction avoids treating arbitrary shell commands, external network access, deployments, or third-party MCP tools as ordinary repository reads/writes. A later integration must define and test a separate explicit policy for those capabilities before enabling them.

## Required Claude Code version and file mentions

- Require Claude Code **v2.1.295 or later** so command-hook `onFailure: "block"` is supported. Without this, a missing or timed-out hook may fail open.
- Claude Code **v2.1.299 or later** supports `CLAUDE_CODE_DISABLE_FILE_MENTIONS=1`. Set this in the user's or administrator's settings/environment, not only in the project settings file: project settings do not apply this environment variable. The TSAR hook checks that the variable is present and equal to `1` before allowing prompts or tools. This disables the `@file` path that can bypass `PreToolUse` Read hooks.
- Example user-level setting in `~/.claude/settings.json` (merge with existing settings):

```json
{
  "env": {
    "CLAUDE_CODE_DISABLE_FILE_MENTIONS": "1"
  }
}
```

Confirm hooks are active with Claude Code's `/hooks` and `/status` commands. Run a controlled negative test before using the profile on a real project.

## Conformance tests

The automated tests verify:

- Prompt blocking when preflight fails.
- Policy-cache hash verification and mandatory reading of every selected file before any other tool.
- Rejection of Bash, PowerShell, subagents, web, MCP, and unknown tools.
- Rejection of path escape and missing write scopes.
- Preservation of Claude Code's native permission prompts.
- Blocking on audit storage failures.
- Post-tool execution evidence.

The CI tests validate the adapter contract. A live Claude Code conformance run is still required before claiming E6 for a particular Claude Code installation.

## Assurance boundary

This integration enforces only the configured Claude Code hook path and the listed tools. It does not control tools exposed outside Claude Code, external processes, direct filesystem changes by the user, or unsupported event paths. The hook audit log is local and is not WORM or cryptographically signed. The session state is protected by local filesystem permissions, not by a separate privileged service.

A policy file being successfully returned by the Read tool proves that Claude Code completed that tool call against the hash-verified cached bytes; it cannot prove the model cognitively understood or obeyed the policy. The hook can enforce tool boundaries and deny unsupported actions, but it cannot guarantee secure generated code.

Official hook behavior and limitations are documented by Anthropic:
- [Claude Code Hooks reference](https://code.claude.com/docs/en/hooks)
- [Claude Code Settings](https://code.claude.com/docs/en/settings)
