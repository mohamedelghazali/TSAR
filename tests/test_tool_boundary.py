from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "tsar-cli"))
from tool_boundary import (
    ActionClass,
    ActionRequest,
    AuthorizationContext,
    AuditWriteError,
    ToolBoundary,
    ToolBoundaryError,
    ToolSpec,
    action_digest,
)


def make_boundary(*, approval=True, audit=None, scopes=None):
    events = [] if audit is None else audit
    spec = ToolSpec(
        name="repo.write",
        action_class=ActionClass.REPOSITORY_WRITE,
        operations=frozenset({"commit"}),
        resources=frozenset({"repo:demo"}),
        required_scope="repo:write",
    )
    sensitive = ToolSpec(
        name="prod.deploy",
        action_class=ActionClass.DEPLOYMENT,
        operations=frozenset({"release"}),
        resources=frozenset({"service:demo"}),
        required_scope="deploy",
    )
    verifier = lambda token, digest, actor: bool(
        approval and token == {"digest": digest, "actor": actor}
    )
    boundary = ToolBoundary(
        {"repo.write": spec, "prod.deploy": sensitive},
        AuthorizationContext("operator-1", frozenset(scopes or {"repo:write", "deploy"})),
        approval_verifier=verifier,
        audit_sink=events.append if isinstance(events, list) else events,
    )
    return boundary, events


def request(**overrides):
    values = dict(
        tool="repo.write",
        operation="commit",
        resource="repo:demo",
        actor="operator-1",
        arguments={"message": "safe change"},
    )
    values.update(overrides)
    return ActionRequest(**values)


def test_registered_scoped_action_dispatches_and_is_audited():
    boundary, events = make_boundary()
    result = boundary.dispatch(request(), lambda args: {"ok": args["message"]})
    assert result == {"ok": "safe change"}
    assert len(events) == 2
    assert events[0]["decision"] == "ALLOW"
    assert "outcome" not in events[0]
    assert events[1]["decision"] == "ALLOW"
    assert events[1]["outcome"] == "EXECUTED"
    assert events[0]["action_sha256"] == events[1]["action_sha256"]
    assert len(events[1]["action_sha256"]) == 64


@pytest.mark.parametrize(
    "changes,reason",
    [
        ({"tool": "unknown.tool"}, "unregistered_tool"),
        ({"operation": "delete"}, "operation_not_registered"),
        ({"resource": "repo:other"}, "resource_out_of_scope"),
        ({"actor": "attacker"}, "actor does not match"),
    ],
)
def test_unknown_or_out_of_scope_actions_are_denied(changes, reason):
    boundary, events = make_boundary()
    called = []
    with pytest.raises(ToolBoundaryError, match=reason):
        boundary.dispatch(request(**changes), lambda args: called.append(args))
    assert called == []
    assert events[-1]["decision"] == "DENY"


def test_missing_scope_denies_action():
    boundary, events = make_boundary(scopes={"repo:read"})
    with pytest.raises(ToolBoundaryError, match="missing_authorization_scope"):
        boundary.dispatch(request(), lambda args: None)
    assert events[-1]["decision"] == "DENY"


def test_deployment_requires_approval_bound_to_exact_action():
    boundary, events = make_boundary()
    req = request(
        tool="prod.deploy",
        operation="release",
        resource="service:demo",
        arguments={"version": "1.2.0"},
        approval={"digest": "wrong", "actor": "operator-1"},
    )
    with pytest.raises(ToolBoundaryError, match="approval"):
        boundary.dispatch(req, lambda args: pytest.fail("must not dispatch"))
    assert events[-1]["reason"] == "missing_or_invalid_action_bound_approval"


def test_valid_action_bound_approval_allows_sensitive_action():
    boundary, _ = make_boundary()
    req = request(
        tool="prod.deploy",
        operation="release",
        resource="service:demo",
        arguments={"version": "1.2.0"},
    )
    token = {"digest": action_digest(req), "actor": "operator-1"}
    req = ActionRequest(**{**req.__dict__, "approval": token})
    assert boundary.dispatch(req, lambda args: "released") == "released"


def test_action_digest_changes_when_arguments_change():
    assert action_digest(request()) != action_digest(request(arguments={"message": "other"}))


def test_non_json_arguments_fail_before_dispatch():
    boundary, _ = make_boundary()
    req = request(arguments={"bad": object()})
    with pytest.raises(ToolBoundaryError, match="canonical JSON"):
        boundary.dispatch(req, lambda args: pytest.fail("must not dispatch"))


def test_audit_failure_before_dispatch_blocks_execution():
    calls = []
    def broken(_event):
        raise OSError("audit unavailable")
    boundary, _ = make_boundary(audit=broken)
    with pytest.raises(AuditWriteError):
        boundary.dispatch(request(), lambda args: calls.append(args))
    assert calls == []


def test_dispatch_error_is_audited_and_propagated():
    boundary, events = make_boundary()
    def fail(_args):
        raise RuntimeError("tool failed")
    with pytest.raises(RuntimeError, match="tool failed"):
        boundary.dispatch(request(), fail)
    assert events[-1]["outcome"] == "DISPATCH_ERROR"
    assert events[-1]["error_type"] == "RuntimeError"
\n\ndef test_authorize_records_allow_without_claiming_execution():
    boundary, events = make_boundary()
    normalized = boundary.authorize(request())
    assert normalized.tool == "repo.write"
    assert len(events) == 1
    assert events[0]["decision"] == "ALLOW"
    assert "outcome" not in events[0]


def test_authorize_denial_is_audited_without_dispatch():
    boundary, events = make_boundary(scopes={"repo:read"})
    with pytest.raises(ToolBoundaryError, match="missing_authorization_scope"):
        boundary.authorize(request())
    assert len(events) == 1
    assert events[0]["decision"] == "DENY"
    assert events[0]["reason"] == "missing_authorization_scope"


def test_record_outcome_is_a_separate_audited_event():
    boundary, events = make_boundary()
    normalized = boundary.authorize(request())
    boundary.record_outcome(normalized, "EXECUTED")
    assert [event.get("outcome") for event in events] == [None, "EXECUTED"]
