"""Deterministic TSAR task planning and lifecycle transition engine.

Classification is a conservative heuristic, not an autonomous security approval.
Explicit domains and impact supplied by an operator take precedence.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import re
from typing import Iterable


class LifecycleState(str, Enum):
    INTAKE = "intake"
    PREFLIGHT = "preflight"
    DESIGN_REVIEW = "design_review"
    IMPLEMENTATION = "implementation"
    VERIFICATION = "verification"
    RELEASE_REVIEW = "release_review"
    COMPLETE = "complete"
    BLOCKED = "blocked"


TRANSITIONS = {
    LifecycleState.INTAKE: {LifecycleState.PREFLIGHT, LifecycleState.BLOCKED},
    LifecycleState.PREFLIGHT: {LifecycleState.DESIGN_REVIEW, LifecycleState.BLOCKED},
    LifecycleState.DESIGN_REVIEW: {LifecycleState.IMPLEMENTATION, LifecycleState.BLOCKED},
    LifecycleState.IMPLEMENTATION: {LifecycleState.VERIFICATION, LifecycleState.BLOCKED},
    LifecycleState.VERIFICATION: {LifecycleState.IMPLEMENTATION, LifecycleState.RELEASE_REVIEW, LifecycleState.BLOCKED},
    LifecycleState.RELEASE_REVIEW: {LifecycleState.COMPLETE, LifecycleState.IMPLEMENTATION, LifecycleState.BLOCKED},
    LifecycleState.BLOCKED: {LifecycleState.PREFLIGHT},
    LifecycleState.COMPLETE: set(),
}

DOMAIN_KEYWORDS = {
    "crypto": ("cryptograph", "encrypt", "decrypt", "cipher", "key management", "signature", "nonce"),
    "ai_security": ("llm", "prompt injection", "model", "agent", "rag", "embedding", "ai "),
    "agentic_ai": ("agent", "tool calling", "multi-agent", "autonomous"),
    "owasp_web": ("web app", "web application", "xss", "csrf", "injection", "http"),
    "api": ("api", "rest", "graphql", "grpc", "websocket"),
    "iam": ("authentication", "authorization", "oauth", "oidc", "login", "session"),
    "data": ("database", "personal data", "pii", "data retention", "migration"),
    "cloud": ("aws", "azure", "gcp", "cloud"),
    "containers": ("docker", "container", "image build"),
    "infrastructure": ("terraform", "kubernetes", "infrastructure", "deployment"),
    "supply_chain": ("dependency", "sbom", "slsa", "provenance", "software supply chain"),
    "testing": ("test", "fuzz", "penetration test", "security test"),
    "development": ("code", "refactor", "software", "repository", "build", "compile"),
    "privacy": ("privacy", "consent", "gdpr", "anonym"),
    "secrets": ("secret", "credential", "token", "password"),
}

HIGH_IMPACT_TERMS = (
    "production", "payment", "financial", "health", "medical", "children",
    "government", "critical infrastructure", "identity document", "private key",
)


@dataclass(frozen=True)
class TaskPlan:
    task: str
    domains: list[str]
    impact: str
    strict_required: bool
    required_gates: list[str]
    classification_basis: str

    def to_dict(self) -> dict:
        return asdict(self)


def classify_task(task: str, explicit_domains: Iterable[str] = (), impact: str = "auto",
                  available_domains: Iterable[str] | None = None) -> TaskPlan:
    if not isinstance(task, str) or not task.strip():
        raise ValueError("task must be a non-empty string")
    if impact not in {"auto", "standard", "high"}:
        raise ValueError("impact must be auto, standard, or high")

    allowed = set(available_domains) if available_domains is not None else None
    chosen = []
    for domain in explicit_domains:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", domain):
            raise ValueError(f"invalid domain name: {domain!r}")
        if allowed is not None and domain not in allowed:
            raise ValueError(f"unknown manifest domain: {domain}")
        if domain not in chosen:
            chosen.append(domain)

    normalized = task.casefold()
    if not chosen:
        for domain, terms in DOMAIN_KEYWORDS.items():
            if allowed is not None and domain not in allowed:
                continue
            if any(term in normalized for term in terms):
                chosen.append(domain)
    if not chosen:
        chosen = ["development"] if allowed is None or "development" in allowed else []

    high = impact == "high" or (
        impact == "auto" and any(term in normalized for term in HIGH_IMPACT_TERMS)
    )
    gates = ["upstream_preflight", "core_policy_review", "applicable_domain_review"]
    if high:
        gates += ["threat_model", "independent_security_review", "release_approval"]
    gates += ["automated_tests", "secret_scan", "secure_code_review", "audit_report"]
    return TaskPlan(
        task=task.strip(),
        domains=chosen,
        impact="high" if high else ("standard" if impact == "standard" else "standard"),
        strict_required=True,
        required_gates=gates,
        classification_basis="operator-supplied domains/impact" if explicit_domains or impact != "auto" else "deterministic keyword heuristic; confirm before implementation",
    )


def validate_transition(current: str | LifecycleState, target: str | LifecycleState) -> tuple[bool, str]:
    try:
        source = LifecycleState(current)
        destination = LifecycleState(target)
    except ValueError as exc:
        return False, f"unknown lifecycle state: {exc}"
    if destination not in TRANSITIONS[source]:
        return False, f"transition {source.value} -> {destination.value} is not permitted"
    return True, "transition permitted"


def transition(current: str | LifecycleState, target: str | LifecycleState,
               *, gates_passed: bool = False) -> LifecycleState:
    allowed, reason = validate_transition(current, target)
    if not allowed:
        raise ValueError(reason)
    if target == LifecycleState.COMPLETE and not gates_passed:
        raise ValueError("completion requires explicit confirmation that all required gates passed")
    return LifecycleState(target)
