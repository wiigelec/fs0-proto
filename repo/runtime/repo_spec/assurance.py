"""Minimal governed semantic-review records for FS0-Core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .errors import AssuranceError

_PHASES = {"Design", "Planning", "Build"}
_DISPOSITIONS = {"PASS", "FAIL"}


@dataclass(frozen=True)
class AssuranceFinding:
    id: str
    disposition: str
    rationale: str
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class AssuranceReport:
    phase: str
    subject_id: str
    disposition: str
    rationale: str
    evidence_refs: tuple[str, ...] = ()
    findings: tuple[AssuranceFinding, ...] = ()

    @property
    def passed(self) -> bool:
        return self.disposition == "PASS"


def make_report(
    *,
    phase: str,
    subject_id: str,
    disposition: str,
    rationale: str,
    evidence_refs: Iterable[str] = (),
    findings: Iterable[AssuranceFinding] = (),
) -> AssuranceReport:
    if phase not in _PHASES:
        raise AssuranceError("invalid-assurance-phase", f"unknown Assurance phase: {phase}")
    if disposition not in _DISPOSITIONS:
        raise AssuranceError("invalid-assurance-disposition", f"unknown Assurance disposition: {disposition}")
    if not isinstance(subject_id, str) or not subject_id:
        raise AssuranceError("invalid-assurance-subject", "Assurance subject identity must be non-empty")
    if not isinstance(rationale, str) or not rationale.strip():
        raise AssuranceError("missing-assurance-rationale", "Assurance report requires rationale")

    finding_tuple = tuple(findings)
    for finding in finding_tuple:
        if finding.disposition not in _DISPOSITIONS:
            raise AssuranceError("invalid-finding-disposition", f"invalid finding disposition: {finding.disposition}")
        if not finding.id or not finding.rationale.strip():
            raise AssuranceError("invalid-assurance-finding", "Assurance findings require identity and rationale")

    if disposition == "PASS" and any(f.disposition == "FAIL" for f in finding_tuple):
        raise AssuranceError("inconsistent-assurance-report", "PASS report cannot contain FAIL findings")

    return AssuranceReport(
        phase,
        subject_id,
        disposition,
        rationale,
        tuple(evidence_refs),
        finding_tuple,
    )


def require_pass(report: AssuranceReport, *, phase: str, subject_id: str) -> None:
    if report.phase != phase or report.subject_id != subject_id:
        raise AssuranceError(
            "assurance-subject-mismatch",
            f"expected {phase} Assurance for {subject_id}, got {report.phase} for {report.subject_id}",
        )
    if not report.passed:
        raise AssuranceError("assurance-failed", f"{phase} Assurance did not pass for {subject_id}")
