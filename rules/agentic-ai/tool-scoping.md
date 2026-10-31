# Agentic Tool Scoping

## Model
Each tool is a capability boundary. The agent receives only the tools required for the current task, with the minimum scope per tool.

## Scoping Dimensions
| Dimension | Control |
|---|---|
| Filesystem | Read-only mount; write to dedicated temp dir |
| Network | Egress allow-list per tool |
| Database | Read replica by default; write via stored procedure only |
| Secrets | Injected per-call, never persisted in agent memory |
| Execution | Ephemeral container, no host mounts, seccomp profile |

## Approval Flow
Irreversible action → human confirmation → short-lived elevated token → action → token revoked.

## Audit
Every tool call logged with: agent ID, tool, scope used, timestamp, input hash, output hash.
