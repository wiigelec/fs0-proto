"""Core normative requirement records and minimal authority primitives."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from .errors import PlanningError, GovernanceError

_NR_ID = re.compile(r"^FS0-NR-[0-9]{3}$")
_FORCE = re.compile(r"\b(SHALL NOT|SHALL|MAY)\b")


@dataclass(frozen=True)
class EvaluationDisposition:
    applicability: str
    rationale: str | None = None


@dataclass(frozen=True)
class NormativeRequirement:
    id: str
    statement: str
    conformance: EvaluationDisposition
    assurance: EvaluationDisposition


@dataclass(frozen=True)
class Authority:
    id: str


@dataclass(frozen=True)
class Delegation:
    source: str
    target: str
    capability: str


def _disposition(value: object, *, dimension: str, requirement_id: str) -> EvaluationDisposition:
    if not isinstance(value, dict):
        raise PlanningError("invalid-applicability", f"{requirement_id} {dimension} evaluation must be an object")
    applicability = value.get("applicability")
    allowed = {"required", "none"}
    if applicability not in allowed:
        raise PlanningError(
            "invalid-applicability",
            f"{requirement_id} {dimension}.applicability must be one of {sorted(allowed)}",
        )
    rationale = value.get("rationale")
    if applicability == "none" and (not isinstance(rationale, str) or not rationale.strip()):
        raise PlanningError(
            "missing-applicability-rationale",
            f"{requirement_id} {dimension}=none requires a rationale",
        )
    if rationale is not None and not isinstance(rationale, str):
        raise PlanningError("invalid-applicability-rationale", f"{requirement_id} {dimension} rationale must be text")
    return EvaluationDisposition(applicability, rationale)


def _normative_forces(statement: str) -> list[str]:
    """Return operative normative forces outside Markdown inline-code spans."""
    visible_parts = statement.split("`")
    visible = "".join(part for index, part in enumerate(visible_parts) if index % 2 == 0)
    return _FORCE.findall(visible)

def parse_requirement(value: object) -> NormativeRequirement:
    if not isinstance(value, dict):
        raise PlanningError("invalid-requirement", "normative requirement must be an object")
    if set(value) != {"id", "statement", "evaluation"}:
        raise PlanningError("invalid-requirement-fields", f"unexpected requirement fields: {sorted(set(value))}")
    rid = value["id"]
    statement = value["statement"]
    if not isinstance(rid, str) or not _NR_ID.fullmatch(rid):
        raise PlanningError("invalid-requirement-id", f"invalid normative requirement ID: {rid!r}")
    if not isinstance(statement, str) or not statement.strip():
        raise PlanningError("invalid-normative-statement", f"{rid} statement must be non-empty text")
    forces = _normative_forces(statement)
    if len(forces) != 1:
        raise PlanningError(
            "invalid-normative-force",
            f"{rid} must contain exactly one recognized SHALL, SHALL NOT, or MAY force",
        )
    evaluation = value["evaluation"]
    if not isinstance(evaluation, dict) or set(evaluation) != {"conformance", "assurance"}:
        raise PlanningError("invalid-evaluation", f"{rid} evaluation must contain conformance and assurance")
    return NormativeRequirement(
        rid,
        statement,
        _disposition(evaluation["conformance"], dimension="conformance", requirement_id=rid),
        _disposition(evaluation["assurance"], dimension="assurance", requirement_id=rid),
    )


def parse_requirements(values: object) -> tuple[NormativeRequirement, ...]:
    if not isinstance(values, list) or not values:
        raise PlanningError("invalid-requirements", "requirements must be a non-empty array")
    requirements = tuple(parse_requirement(value) for value in values)
    ids = [r.id for r in requirements]
    if len(ids) != len(set(ids)):
        raise PlanningError("duplicate-requirement-id", "normative requirement IDs must be unique")
    return requirements


class AuthorizationGraph:
    """Minimal explicit-delegation graph with default-deny lookup."""

    def __init__(self, authorities: Iterable[Authority], delegations: Iterable[Delegation] = ()) -> None:
        self._authorities = {a.id for a in authorities}
        self._delegations = tuple(delegations)
        if len(self._authorities) == 0:
            raise GovernanceError("missing-authority", "at least one explicit authority is required")
        for edge in self._delegations:
            if edge.source not in self._authorities or edge.target not in self._authorities:
                raise GovernanceError("unresolved-delegation", "delegation endpoints must resolve to explicit authorities")

    def authorized(self, actor: str, capability: str, *, authority: str) -> bool:
        if actor == authority and actor in self._authorities:
            return True
        return any(
            d.source == authority and d.target == actor and d.capability == capability
            for d in self._delegations
        )

    def require(self, actor: str, capability: str, *, authority: str) -> None:
        if not self.authorized(actor, capability, authority=authority):
            raise GovernanceError(
                "authorization-denied",
                f"{actor} has no explicit {capability!r} authorization from {authority}",
            )
