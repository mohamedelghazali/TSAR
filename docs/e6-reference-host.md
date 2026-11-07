# E6: Reference Host Integration and End-to-End Conformance

## Objective

E6 is a host-integration profile that composes the existing E2-E5 controls on one controlled execution path. It addresses the gap between independently tested building blocks and a host that actually connects them.

The reference implementation is `tools/tsar-cli/reference_host.py`, packaged as `reference_host` in the TSAR CLI distribution.

## Controlled execution sequence

1. **E2 preflight:** initialize a strict lifecycle run. The upstream verifier resolves one immutable TSAR commit and fails closed when the manifest, core directives, selected domains, or active-file inventory cannot be verified.
2. **Policy injection:** fetch the manifest and every required core/selected-domain file from the exact pinned commit. Recompute SHA-256 for every file and compare it with the verifier's recorded inventory. Pass the verified UTF-8 policy contents and mandatory read instruction to the host's agent callback before implementation.
3. **E3 tool boundary:** expose only the host-provided `dispatch_tool` function to the agent callback. The host supplies a trusted tool registry, explicit dispatch functions, authenticated principal/scopes, action-bound approval verification, and an audit sink. Model-supplied actor identity is never accepted.
4. **E4 output verification:** after the agent callback returns, obtain changed files from a host-owned collector. Reject files outside the project root, symlink paths, and empty change sets. Run every trusted configured command without a shell; at minimum require secret scanning, secure code review, and repository tests. Record command exit codes and output digests.
5. **E5 reviewer lifecycle:** write output-verification evidence. The `output_verification` lifecycle gate remains `PENDING` until an authorized reviewer signs the exact evidence through the existing Ed25519 lifecycle workflow. TSAR does not generate or hold reviewer private keys.

## API contract

`ReferenceHost` requires:

- A project root containing `manifest.yaml` and `tools/tsar-cli/verify_upstream.py`.
- A trusted mapping of `ToolSpec` entries to host-owned dispatcher callables. The mapping keys must match exactly.
- An authenticated `AuthorizationContext`.
- An action-bound approval verifier and a durable audit sink.
- Trusted `CheckCommand` objects for `secret_scan`, `secure_code_review`, and `tests`.
- A host-owned changed-file collector invoked after the agent callback.

The `agent` callback receives a frozen `HostContext` containing the immutable TSAR commit, manifest version, selected domains, read-only policy text, mandatory policy instruction, and guarded tool dispatcher. The callback is synchronous. Do not pass raw provider tools, filesystem writers, shell access, credentials, or deployment clients around the guarded dispatcher.

Example configuration:

```python
from reference_host import CheckCommand, ReferenceHost
from tool_boundary import AuthorizationContext, ToolSpec, ActionClass

registry = {
    "workspace.read": ToolSpec(
        name="workspace.read",
        action_class=ActionClass.READ_ONLY,
        operations=frozenset({"read"}),
        resources=frozenset({"project:current"}),
        required_scope="project:read",
    ),
}

host = ReferenceHost(
    repo_root=project_root,
    tool_registry=registry,
    dispatchers={"workspace.read": trusted_read_dispatcher},
    authorization=AuthorizationContext(
        principal=authenticated_user_id,
        scopes=frozenset({"project:read"}),
    ),
    approval_verifier=verify_action_bound_approval,
    audit_sink=durable_audit_sink,
    required_checks=[
        CheckCommand("secret_scan", ("python", "skills/secret-scanner/scanner.py", "."),
                     "tsar-secret-scanner", "pinned-version"),
        CheckCommand("secure_code_review", ("python", "skills/secure-review/review.py", "."),
                     "tsar-secure-review", "pinned-version"),
        CheckCommand("tests", ("pytest", "-q"), "pytest", "pinned-version"),
    ],
)

result = host.run_task(
    "Implement a secure API endpoint",
    agent=invoke_model_with_context_and_tools,
    task_id="task-2026-001",
    agent_id="your-host-agent",
    audit_file=".tsar/runs/task-2026-001.json",
    output_evidence_file=".tsar/evidence/task-2026-001-output.json",
    changed_files_provider=collect_changed_files_from_host_vcs,
    domains=["api", "iam"],
)
if result.status != "PASS":
    raise RuntimeError("TSAR blocked output acceptance")
```

The example dispatcher, approval verifier, durable audit sink, model invocation, and VCS collector are host responsibilities. They must be implemented with the target runtime's authenticated APIs and tested for bypasses; the example does not create those integrations automatically.

## E6 conformance requirements

A host may claim E6 only for the exact runtime and execution paths that pass tests demonstrating:

1. Preflight failure prevents agent invocation.
2. The policy content injected into the agent context is fetched from one immutable commit and every byte hash matches preflight evidence.
3. Missing, stale, mixed-commit, or modified policy content blocks invocation.
4. The agent-facing tool surface contains only guarded dispatch functions; all exposed tool calls are routed through `ToolBoundary`.
5. Unregistered tools, wrong principals, missing scopes, out-of-scope resources, invalid approvals, and audit-sink failures prevent dispatch.
6. The host obtains the changed-file set independently of model output and rejects path escape, symlinks, missing files, and empty sets.
7. Required checks execute as real processes from trusted configuration without shell interpolation.
8. Failed, missing, skipped, timed-out, or unexecutable checks prevent acceptance and produce BLOCKED evidence where an evidence artifact can safely be written.
9. Passing output evidence is bound to pinned TSAR provenance and remains pending until an authorized external Ed25519 reviewer attests the E5 gate.
10. Tests exercise the real host invocation path and attempt to bypass each boundary.

## Assurance boundary

- E6 proves only the tested host adapter path. It does not intercept tools or writes the host exposes elsewhere.
- Passing policy text to an agent does not prove that a model cognitively read, understood, or obeyed it. The host can prove retrieval, hash validation, and context injection; only runtime controls can enforce tool actions.
- A Python callback is not a sandbox. The host must not expose alternate unrestricted capabilities to the model, and must isolate the model process if stronger containment is required.
- A successful `ReferenceHost` run means the configured output checks passed. It does **not** mean the lifecycle is complete: reviewer signatures and every other required lifecycle gate remain mandatory.
- Local evidence and callback-based audit sinks are not automatically immutable. Production hosts must provide durable, access-controlled audit storage and protect check configuration, dispatcher registration, VCS change discovery, and reviewer trust material.
- No universal E6 claim is made for closed or chat-only agents without a supported host integration.

## Current implementation status

The reference adapter and automated conformance tests are provided as reusable building blocks. A provider-specific E6 claim requires a concrete host integration and a bypass-tested conformance run in that host. The repository's own tests validate the reference adapter contract; they do not establish that external providers use it.
