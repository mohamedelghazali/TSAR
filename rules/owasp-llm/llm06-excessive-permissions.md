# LLM06: Excessive Permissions

## Principle
The model and its agent framework must operate with the minimum permissions
required. Permissions granted to the LLM are permissions an attacker can
obtain via prompt injection.

## Controls
- Per-tool permission scoping; no wildcard on any tool.
- Default read-only for data tools; write requires elevation.
- Short-lived tokens for tool credentials (<= 15 minutes).
- Human-in-the-loop for irreversible actions (delete, transfer, deploy, execute).
- Separate identities for planning vs execution.
- No direct access to production credentials from the model runtime.
- Sandbox code execution; no filesystem or network beyond explicit mounts.

## Least-Privilege Matrix
| Tool | Default | Elevation |
|---|---|---|
| Database | Read replica | Stored procedure only |
| Filesystem | Read-only workspace | Write to temp dir |
| Network | Allow-list egress | Explicit approval |
| Shell | Disabled | Sandbox only |
| Secrets | Not accessible | Delegated, per-call |

## Monitoring
- Log every tool call: agent, tool, scope, timestamp, parameters hash.
- Alert on privilege escalation attempts.
- Alert on tool calls outside declared scope.

## Forbidden
- Wildcard permissions on any tool.
- Long-lived credentials embedded in agent config.
- Agents with simultaneous access to secrets and external network.
- Unattended irreversible actions.
