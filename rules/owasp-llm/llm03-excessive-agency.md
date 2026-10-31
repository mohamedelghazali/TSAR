# LLM03: Excessive Agency

## Principle
An agent's authority MUST NOT exceed the minimum required to complete the task.

## Controls
- Tool allow-list: only explicitly approved tools are callable.
- Per-tool scopes: database tool gets read-only by default; write requires elevation.
- Short-lived tokens: <=15 minutes for tool credentials.
- Human-in-the-loop: required for delete, transfer, deploy, execute, send-email, and permission changes.
- Sandboxing: code execution runs in ephemeral, network-restricted containers.
- Rate limits: per-agent and per-tool quotas to prevent resource exhaustion.

## Forbidden
- Wildcard permissions (`*`) on any agent tool.
- Long-lived credentials embedded in agent configuration.
- Agents with simultaneous access to secrets, production data, and external network.
