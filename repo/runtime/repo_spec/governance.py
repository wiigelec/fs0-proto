"""Explicit non-circular Governance acceptance and lineage."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

from .assurance import AssuranceReport, require_pass as require_assurance_pass
from .conformance import ConformanceReport, require_pass as require_conformance_pass
from .errors import GovernanceError
from .normative import AuthorizationGraph

@dataclass(frozen=True)
class AcceptanceRecord:
    acceptance_id: str
    stage: str
    subject_id: str
    actor: str
    decision: str
    predecessor_authority: str
    evidence_refs: tuple[str, ...]
    resulting_state: str

    def to_dict(self) -> dict:
        return {
            "schema_version": "1",
            "artifact_type": "acceptance",
            "acceptance_id": self.acceptance_id,
            "stage": self.stage,
            "subject_id": self.subject_id,
            "actor": self.actor,
            "decision": self.decision,
            "predecessor_authority": self.predecessor_authority,
            "evidence_refs": list(self.evidence_refs),
            "resulting_state": self.resulting_state,
        }

def accept(
    *,
    acceptance_id: str,
    stage: str,
    subject_id: str,
    actor: str,
    predecessor_authority: str,
    resulting_state: str,
    authority_graph: AuthorizationGraph,
    conformance: ConformanceReport,
    assurance: AssuranceReport,
    evidence_refs: Iterable[str] = (),
) -> AcceptanceRecord:
    if stage not in {"Planning", "Build"}:
        raise GovernanceError("invalid-acceptance-stage", f"unsupported acceptance stage: {stage}")
    if not all((acceptance_id, subject_id, actor, predecessor_authority, resulting_state)):
        raise GovernanceError("incomplete-acceptance", "acceptance identity, subject, actor, predecessor authority, and resulting state are required")
    authority_graph.require(actor, f"accept:{stage}", authority=predecessor_authority)
    require_conformance_pass(conformance)
    require_assurance_pass(assurance, phase=stage, subject_id=subject_id)
    refs = tuple(evidence_refs)
    if not refs:
        raise GovernanceError("missing-acceptance-evidence", "acceptance requires explicit evidence references")
    if resulting_state == predecessor_authority:
        raise GovernanceError("circular-acceptance", "candidate resulting state cannot be its own predecessor authority")
    return AcceptanceRecord(
        acceptance_id, stage, subject_id, actor, "ACCEPT",
        predecessor_authority, refs, resulting_state,
    )
