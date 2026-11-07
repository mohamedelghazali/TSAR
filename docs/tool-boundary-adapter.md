# Tool Boundary Adapter

`tools/tsar-cli/tool_boundary.py` provides a reusable fail-closed dispatch boundary for host integrations that control tool invocation. It is an E3 building block, not a universal agent interceptor.

## Trust boundary

The host integration MUST own and protect:

- The immutable tool registry (`ToolSpec`), including action class, operations, exact resource allowlist, and required authorization scope.
- The authenticated principal and scopes (`AuthorizationContext`). Never derive either from model output.
- The approval verifier. For credential access, deployment, irreversible actions, or tools marked `requires_approval`, it must verify a host-authenticated, single-action approval bound to the supplied action SHA-256 and principal. A boolean supplied by the model is not approval.
- The audit sink. It should append events to an access-controlled durable log. The library emits no argument values or secrets in audit events.
- The actual dispatcher. Every tool invocation must pass through `ToolBoundary.dispatch`; bypass paths are outside coverage.

Unknown tools, unregistered operations, resources outside the exact allowlist, mismatched actors, missing scopes, invalid approvals, and non-canonical JSON arguments are rejected. The action digest covers tool, operation, resource, actor, and canonical arguments. The dispatcher receives a JSON snapshot of the arguments covered by that digest.

## Failure semantics

The boundary writes a decision event before dispatch. If that write fails, dispatch is blocked. It writes an outcome event after dispatch. If the outcome write fails, the action may already have executed; the raised `AuditWriteError` deliberately does not claim rollback. A dispatch exception is recorded and re-raised.

## Integration requirements

1. Run the `agent-gate` preflight before task execution.
2. Load verified TSAR policy context into the host-supported agent context mechanism.
3. Register each exposed tool in trusted host code; do not accept model-supplied classifications, scopes, resource allowlists, or approval state.
4. Route every call through the boundary and preserve the host platform's permission and approval controls.
5. Add host conformance tests proving that the real tool dispatch path cannot bypass this boundary.
6. Report E3 only for the specific tools and paths actually wrapped. If any tool bypasses the wrapper, disclose it and do not claim full E3 coverage.

The current module is a library boundary, not a sandbox, network firewall, credential vault, OS permission system, or provider-level control. It cannot intercept tools in arbitrary closed agents or constrain a process that can call the underlying tool directly. The host must enforce that architectural separation.
