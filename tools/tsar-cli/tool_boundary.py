"""Fail-closed tool/action dispatch boundary for controlled agent integrations.

The host integration owns the tool registry, principal/scopes, approval verifier,
audit sink, and dispatcher. Model-provided labels or arguments never grant access.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Mapping


class ActionClass(str, Enum):
    READ_ONLY = "read_only"
    REPOSITORY_WRITE = "repository_write"
    EXTERNAL_NETWORK = "external_network"
    CREDENTIAL_ACCESS = "credential_access"
    DEPLOYMENT = "deployment"
    IRREVERSIBLE = "irreversible"


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class ToolBoundaryError(RuntimeError):
    """A tool action was denied or could not be safely dispatched."""


class AuditWriteError(ToolBoundaryError):
    """The audit sink failed; callers must not assume the action was not executed."""


@dataclass(frozen=True)
class ToolSpec:
    """Trusted host-side registration; never construct this from model output."""
    name: str
    action_class: ActionClass
    operations: frozenset[str]
    resources: frozenset[str]
    required_scope: str
    requires_approval: bool = False


@dataclass(frozen=True)
class ActionRequest:
    tool: str
    operation: str
    resource: str
    actor: str
    arguments: Mapping[str, Any]
    approval: Any = None


@dataclass(frozen=True)
class AuthorizationContext:
    principal: str
    scopes: frozenset[str]


SENSITIVE_CLASSES = frozenset({
    ActionClass.CREDENTIAL_ACCESS,
    ActionClass.DEPLOYMENT,
    ActionClass.IRREVERSIBLE,
})


def action_digest(request: ActionRequest) -> str:
    """Hash the exact action identity and arguments; do not include approval data."""
    try:
        canonical = json.dumps(
            {
                "tool": request.tool,
                "operation": request.operation,
                "resource": request.resource,
                "actor": request.actor,
                "arguments": request.arguments,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ToolBoundaryError("Action arguments are not canonical JSON data") from exc
    return hashlib.sha256(canonical).hexdigest()


class ToolBoundary:
    """Authorize registered actions independently from dispatching them.

    Hosts with native pre-tool hooks call authorize() before the provider executes
    the tool, then record_outcome() from the corresponding post-tool event.
    """

    def __init__(
        self,
        registry: Mapping[str, ToolSpec],
        authorization: AuthorizationContext,
        *,
        approval_verifier: Callable[[Any, str, str], bool],
        audit_sink: Callable[[Mapping[str, Any]], None],
    ) -> None:
        self._registry = dict(registry)
        self._authorization = authorization
        self._approval_verifier = approval_verifier
        self._audit_sink = audit_sink

    def _audit(self, event: Mapping[str, Any]) -> None:
        try:
            self._audit_sink(dict(event))
        except Exception as exc:
            raise AuditWriteError(
                "Audit sink failed; dispatch is blocked or its outcome may be unknown"
            ) from exc

    def authorize(self, request: ActionRequest) -> ActionRequest:
        """Audit and authorize an action without executing its underlying tool."""
        if not isinstance(request, ActionRequest):
            raise ToolBoundaryError("Invalid action request")
        if request.actor != self._authorization.principal:
            self._audit({
                "schema": "tsar/tool-boundary-event/v1",
                "decision": Decision.DENY.value,
                "tool": request.tool,
                "operation": request.operation,
                "resource": request.resource,
                "actor": self._authorization.principal,
                "claimed_actor": request.actor,
                "action_sha256": None,
                "reason": "actor_mismatch",
            })
            raise ToolBoundaryError("Action actor does not match authenticated principal")
        if not isinstance(request.arguments, Mapping):
            raise ToolBoundaryError("Action arguments must be a mapping")
        try:
            argument_snapshot = json.loads(json.dumps(
                request.arguments, sort_keys=True, separators=(",", ":"),
                ensure_ascii=False, allow_nan=False,
            ))
        except (TypeError, ValueError) as exc:
            raise ToolBoundaryError("Action arguments are not canonical JSON data") from exc
        normalized = ActionRequest(
            tool=request.tool, operation=request.operation, resource=request.resource,
            actor=request.actor, arguments=argument_snapshot, approval=request.approval,
        )
        spec = self._registry.get(normalized.tool)
        digest = action_digest(normalized)

        reason = None
        if spec is None:
            reason = "unregistered_tool"
        elif normalized.operation not in spec.operations:
            reason = "operation_not_registered"
        elif normalized.resource not in spec.resources:
            reason = "resource_out_of_scope"
        elif spec.required_scope not in self._authorization.scopes:
            reason = "missing_authorization_scope"
        elif (
            spec.requires_approval or spec.action_class in SENSITIVE_CLASSES
        ) and not self._approval_verifier(
            normalized.approval, digest, self._authorization.principal
        ):
            reason = "missing_or_invalid_action_bound_approval"

        event = {
            "schema": "tsar/tool-boundary-event/v1",
            "decision": Decision.DENY.value if reason else Decision.ALLOW.value,
            "tool": normalized.tool,
            "operation": normalized.operation,
            "resource": normalized.resource,
            "actor": self._authorization.principal,
            "action_sha256": digest,
            "reason": reason,
        }
        self._audit(event)
        if reason:
            raise ToolBoundaryError(f"Tool action denied: {reason}")
        return normalized

    def record_outcome(
        self,
        request: ActionRequest,
        outcome: str,
        *,
        error_type: str | None = None,
    ) -> None:
        """Record a provider-side tool outcome after a prior authorization."""
        if outcome not in {"EXECUTED", "DISPATCH_ERROR"}:
            raise ToolBoundaryError("Unsupported tool outcome")
        event = {
            "schema": "tsar/tool-boundary-event/v1",
            "decision": Decision.ALLOW.value,
            "tool": request.tool,
            "operation": request.operation,
            "resource": request.resource,
            "actor": self._authorization.principal,
            "action_sha256": action_digest(request),
            "outcome": outcome,
        }
        if error_type is not None:
            event["error_type"] = error_type
        self._audit(event)

    def dispatch(
        self,
        request: ActionRequest,
        dispatcher: Callable[[Mapping[str, Any]], Any],
    ) -> Any:
        """Authorize, dispatch, and record the outcome as one controlled call."""
        normalized = self.authorize(request)
        try:
            result = dispatcher(normalized.arguments)
        except Exception as exc:
            self.record_outcome(
                normalized, "DISPATCH_ERROR", error_type=type(exc).__name__
            )
            raise
        self.record_outcome(normalized, "EXECUTED")
        return result
