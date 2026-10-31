# Advanced AI Agent Security

## Scope
Multi-agent systems, autonomous coding agents, computer-use agents,
long-running agents with memory and tool use.

## Isolation
- Each agent runs in its own sandbox (container, VM, or microVM).
- Filesystem access limited to a dedicated workspace.
- Network egress via allow-listed proxy only.
- No access to production credentials; use delegated tokens.

## Tool Permissions
- Per-tool scoping with explicit allow-list.
- Every tool call logged with parameters and result hash.
- Irreversible actions require human approval (delete, deploy, transfer).
- Tools run with the minimum OS privileges (non-root, seccomp, AppArmor).

## Memory
- Memory partitioned per agent, per user, per task.
- Write validation: schema, length, content filters.
- TTL per memory entry; no indefinite retention.
- Retrieved memory treated as untrusted data.

## Multi-Agent
- Inter-agent messages signed and authenticated.
- Consensus required for high-impact decisions.
- No single agent has both read access to secrets and write access to external systems.
- Monitor for prompt injection propagation across agents.

## Computer-Use Agents
- Isolated desktop environment (VM) for UI interaction.
- No access to host clipboard, filesystem, or credentials.
- Screen recording for audit; retention per policy.
- Human confirmation for privileged UI actions.

## Oversight
- Every agent action auditable.
- Kill switch available at all times.
- Periodic review of agent decisions.
- Alignment checks: agents refuse harmful requests regardless of instructions.

## Forbidden
- Agents with `*` permissions.
- Long-lived credentials in agent config.
- Agents with simultaneous access to secrets and external network.
- Unattended irreversible actions.
- Unbounded execution time or cost.
