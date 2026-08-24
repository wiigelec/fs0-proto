#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REVIEW_TYPES = {
    "requirement-quality", "ambiguity", "contradiction", "Design-fidelity",
    "Plan-fidelity", "Build-fidelity", "Conformance-interpretation",
    "evidence-sufficiency",
}
FINDING_STATUSES = {"satisfied", "defect", "insufficient", "governance-required"}
CASES_DIR = "repo/assurance/cases"
FINDINGS_DIR = "repo/assurance/findings"


class AssuranceError(ValueError):
    pass


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_case(record):
    required = {
        "schema_version", "record_type", "case_id", "authorizing_authority_id",
        "review_obligation_id", "review_type", "reviewed_subject", "evidence",
        "finding_identity",
    }
    if not isinstance(record, dict) or not required <= set(record):
        raise AssuranceError("Assurance case lacks required fields")
    if record["schema_version"] != "1" or record["record_type"] != "assurance-review-case":
        raise AssuranceError("invalid Assurance case envelope")
    for key in ("case_id", "authorizing_authority_id", "review_obligation_id", "finding_identity"):
        if not _nonempty(record.get(key)):
            raise AssuranceError(f"{key} must be non-empty")
    if record.get("review_type") not in REVIEW_TYPES:
        raise AssuranceError("invalid Assurance review_type")
    if not isinstance(record["reviewed_subject"], dict) or not record["reviewed_subject"]:
        raise AssuranceError("reviewed_subject must be a non-empty object")
    if not isinstance(record["evidence"], list):
        raise AssuranceError("evidence must be a list")
    exclusions = record.get("material_exclusions")
    if exclusions is not None and not isinstance(exclusions, list):
        raise AssuranceError("material_exclusions must be a list when present")
    if record["reviewed_subject"].get("authority_id") == record["authorizing_authority_id"]:
        raise AssuranceError("review subject cannot authorize its own review")
    return record


def validate_finding(record):
    required = {"schema_version", "record_type", "finding_id", "case_id", "status", "sequence"}
    if not isinstance(record, dict) or not required <= set(record):
        raise AssuranceError("Assurance finding lacks required fields")
    if record["schema_version"] != "1" or record["record_type"] != "assurance-finding":
        raise AssuranceError("invalid Assurance finding envelope")
    if not _nonempty(record.get("finding_id")) or not _nonempty(record.get("case_id")):
        raise AssuranceError("finding_id and case_id must be non-empty")
    if record.get("status") not in FINDING_STATUSES:
        raise AssuranceError("invalid Assurance finding status")
    if not isinstance(record.get("sequence"), int) or record["sequence"] < 1:
        raise AssuranceError("finding sequence must be positive")
    return record


def triggered_obligation_ids(correspondence_records, subject_requirement_ids):
    subject_ids = set(subject_requirement_ids)
    out = []
    for record in correspondence_records:
        if record.get("requirement_id") in subject_ids and record.get("applicability") == "required":
            out.extend(record.get("obligation_ids", []))
    return out



def instantiate_review_cases(
    work_id,
    subject_requirement_ids,
    correspondence_records,
    obligation_records,
    authorizing_authority_id,
    review_type_by_obligation,
    evidence,
    candidate_sha=None,
):
    if not _nonempty(work_id) or not _nonempty(authorizing_authority_id):
        raise AssuranceError("work_id and authorizing_authority_id must be non-empty")
    if not isinstance(review_type_by_obligation, dict):
        raise AssuranceError("review_type_by_obligation must be an object")
    if not isinstance(evidence, list):
        raise AssuranceError("evidence must be a list")
    if candidate_sha is not None:
        if not isinstance(candidate_sha, str) or len(candidate_sha) != 40 or any(ch not in "0123456789abcdefABCDEF" for ch in candidate_sha):
            raise AssuranceError("candidate_sha must be an exact Git SHA when supplied")
        candidate_sha = candidate_sha.lower()

    obligation_by_id = {
        item.get("obligation_id"): item
        for item in obligation_records
        if isinstance(item, dict) and _nonempty(item.get("obligation_id"))
    }
    triggered = triggered_obligation_ids(correspondence_records, subject_requirement_ids)
    cases = []
    for obligation_id in triggered:
        obligation = obligation_by_id.get(obligation_id)
        if obligation is None:
            raise AssuranceError(f"triggered obligation does not resolve: {obligation_id}")
        review_type = review_type_by_obligation.get(obligation_id)
        if review_type not in REVIEW_TYPES:
            raise AssuranceError(f"triggered obligation lacks supported review type: {obligation_id}")
        digest = hashlib.sha256(f"{work_id}\0{obligation_id}".encode("utf-8")).hexdigest()[:24]
        reviewed_subject = {"work_id": work_id, "requirement_id": obligation.get("requirement_id")}
        if candidate_sha is not None:
            reviewed_subject["candidate_sha"] = candidate_sha
        case = {
            "schema_version": "1", "record_type": "assurance-review-case",
            "case_id": f"FS0-CASE-{digest}",
            "authorizing_authority_id": authorizing_authority_id,
            "review_obligation_id": obligation_id, "review_type": review_type,
            "reviewed_subject": reviewed_subject, "evidence": list(evidence),
            "material_exclusions": [], "finding_identity": f"FS0-FINDING-{digest}-1",
        }
        cases.append(validate_case(case))
    return cases


def write_case(root, record):
    case = validate_case(dict(record))
    directory = Path(root) / CASES_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{case['case_id']}.json"
    path.write_text(json.dumps(case, indent=2) + "\\n", encoding="utf-8")
    return path


def write_finding(root, record):
    finding = validate_finding(dict(record))
    directory = Path(root) / FINDINGS_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{finding['finding_id']}.json"
    path.write_text(json.dumps(finding, indent=2) + "\\n", encoding="utf-8")
    return path


def resolution_status(case_id, findings):
    relevant = [validate_finding(dict(x)) for x in findings if x.get("case_id") == case_id]
    if not relevant:
        return "missing"
    seqs = [x["sequence"] for x in relevant]
    if len(seqs) != len(set(seqs)):
        raise AssuranceError("finding sequence must be unique within a case")
    latest = max(relevant, key=lambda x: x["sequence"])
    return "resolved" if latest["status"] == "satisfied" else "adverse"


def load_artifacts(root, relative_dir, validator):
    directory = Path(root) / relative_dir
    if not directory.exists():
        return []
    if not directory.is_dir():
        raise AssuranceError(f"{relative_dir} must be a directory")
    records = []
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.suffix != ".json":
            raise AssuranceError(f"unexpected Assurance artifact: {path}")
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AssuranceError(f"invalid Assurance artifact {path}: {exc}") from exc
        records.append(validator(record))
    return records


def load_cases(root):
    return load_artifacts(root, CASES_DIR, validate_case)


def load_findings(root):
    return load_artifacts(root, FINDINGS_DIR, validate_finding)
