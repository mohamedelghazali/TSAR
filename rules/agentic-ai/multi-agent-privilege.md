# Multi-Agent Privilege Separation

## Principle
No single agent should hold enough privilege to complete a harmful action alone.
Privileges are partitioned across agents; high-impact actions require consensus.

## Role Partitioning
| Role | Permissions | Cannot |
|---|---|---|
| Planner | Read context, emit plan | Execute tools |
| Executor | Invoke approved tools | Read secrets |
| Auditor | Read all events | Mutate state |
| Approver | Approve high-impact actions | Execute without second approver |

At least two distinct roles must be involved in any irreversible action.

## Delegation
- Delegation tokens are short-lived (<= 15 minutes) and scoped to a single task.
- Delegated token inherits the intersection of delegator and delegatee permissions.
- Delegation chain is logged: who delegated to whom, for what, until when.
- No transitive delegation beyond depth 2 without explicit policy.

## Consensus for High-Impact Actions
| Action | Required Approvals |
|---|---|
| Delete production data | 2 distinct human approvers |
| Deploy to production | 1 human + 1 automated policy check |
| Transfer funds | 2 human approvers, out-of-band |
| Change IAM policy | 1 human + security team approval |

Consensus is enforced by a policy engine, not by agent instructions.

## Message Authentication
- Every inter-agent message is signed (Ed25519) by the sender's workload identity.
- Receiver verifies signature before processing.
- Message includes: sender ID, recipient ID, task ID, timestamp, nonce, payload hash.
- Replay protection: nonce tracked per task; messages older than 5 minutes rejected.

## Information Flow Control
- Agents are labeled with a security level (public, internal, confidential, restricted).
- An agent may only read data at or below its label.
- An agent may only send data to agents at or above the data's label.
- Flow policy enforced at the message bus, not by agent code.

## Prompt Injection Propagation
- Retrieved content and tool outputs are marked untrusted; agents treat them as data.
- An agent receiving untrusted content cannot elevate its own permissions.
- Cross-agent prompt injection detected by: message content classification, capability mismatch, anomaly detection on tool calls.

## Monitoring
- Every action logs: agent ID, role, task ID, tool, parameters hash, result hash.
- Alerts on:
  - Agent invoking a tool outside its role.
  - Delegation depth > 2.
  - Consensus bypass attempts.
  - Sudden privilege escalation by any agent.
  - Cross-label data flow violations.

## Kill Switch
- A single authenticated action disables all agents in a namespace.
- Kill switch requires two-person approval.
- Disabling logs the reason, the operator, and the affected agents.

## Forbidden
- Agents with permission to both read secrets and write to external systems.
- Single-agent approval for irreversible actions.
- Unsigned inter-agent messages.
- Bypassing the policy engine "for latency".
- Long-lived delegation tokens.
