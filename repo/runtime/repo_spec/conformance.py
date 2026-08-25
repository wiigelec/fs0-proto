"""Mechanical Conformance surfaces for the FS0 workflow."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

from .errors import ConformanceError
from .plan import LogicalPlan, load_plan
from .functional_set import load_functional_set
from .design import load_design_input
from .repository import Repository

@dataclass(frozen=True)
class ConformanceFinding:
    code: str
    message: str
    path: str | None = None

@dataclass(frozen=True)
class ConformanceReport:
    report_id: str
    subject_type: str
    subject_id: str
    disposition: str
    evidence_refs: tuple[str, ...] = ()
    findings: tuple[ConformanceFinding, ...] = ()

    @property
    def passed(self) -> bool:
        return self.disposition == "PASS"

    def to_dict(self) -> dict:
        return {
            "schema_version": "1",
            "artifact_type": "conformance-report",
            "report_id": self.report_id,
            "subject": {"type": self.subject_type, "id": self.subject_id},
            "disposition": self.disposition,
            "evidence_refs": list(self.evidence_refs),
            "findings": [
                {"code": f.code, "message": f.message, **({"path": f.path} if f.path else {})}
                for f in self.findings
            ],
        }

def _pass(subject_type: str, subject_id: str, evidence_refs: Iterable[str] = ()) -> ConformanceReport:
    return ConformanceReport(
        f"CONF-{subject_type.upper()}-{subject_id}",
        subject_type,
        subject_id,
        "PASS",
        tuple(evidence_refs),
        (),
    )

def design_conformance(repository: Repository, design_input: dict) -> ConformanceReport:
    proposal = load_design_input(repository, design_input)
    return _pass("design", proposal.doc_id, (f"{proposal.revision}:{proposal.path}",))

def functional_set_conformance(repository: Repository, path: str) -> ConformanceReport:
    fs = load_functional_set(path, repository)
    return _pass("functional-set", fs.id, (path,))

def plan_conformance(repository: Repository, path: str) -> tuple[LogicalPlan, ConformanceReport]:
    plan = load_plan(path, repository)
    return plan, _pass("plan", plan.id, (path,))

def require_pass(report: ConformanceReport, *, subject_type: str | None = None, subject_id: str | None = None) -> None:
    if subject_type is not None and report.subject_type != subject_type:
        raise ConformanceError("conformance-subject-type-mismatch", f"expected {subject_type}, got {report.subject_type}")
    if subject_id is not None and report.subject_id != subject_id:
        raise ConformanceError("conformance-subject-id-mismatch", f"expected {subject_id}, got {report.subject_id}")
    if not report.passed:
        raise ConformanceError("conformance-failed", f"Conformance did not pass for {report.subject_id}")

def build_conformance(plan: LogicalPlan, manifest: dict) -> ConformanceReport:
    if not isinstance(manifest, dict) or manifest.get("artifact_type") != "build-manifest":
        raise ConformanceError("invalid-build-manifest", "Build manifest must be a build-manifest object")
    if manifest.get("plan_id") != plan.id:
        raise ConformanceError("build-manifest-plan-mismatch", "Build manifest plan_id does not match accepted Plan")
    if manifest.get("implementation_predecessor") != plan.implementation_predecessor:
        raise ConformanceError(
            "build-manifest-predecessor-mismatch",
            "Build manifest implementation_predecessor does not match accepted Plan",
        )

    mutations = manifest.get("mutations")
    if not isinstance(mutations, list):
        raise ConformanceError("invalid-build-mutations", "Build manifest mutations must be an array")

    planned = {(fc.path, fc.operation) for fc in plan.file_changes}
    observed = set()
    for item in mutations:
        if not isinstance(item, dict):
            raise ConformanceError("invalid-build-mutation", "Build manifest mutations must be objects")
        pair = (item.get("path"), item.get("operation"))
        if pair not in planned:
            raise ConformanceError("unauthorized-build-mutation", f"unplanned mutation: {pair}")
        if pair in observed:
            raise ConformanceError("duplicate-build-mutation", f"duplicate mutation: {pair}")
        observed.add(pair)

    missing = sorted(planned - observed)
    if missing:
        raise ConformanceError(
            "missing-build-mutation",
            f"planned mutations absent from Build manifest: {missing}",
        )
    return _pass("build", manifest.get("build_id", "unknown"), (plan.id,))
