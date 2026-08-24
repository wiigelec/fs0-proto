#!/usr/bin/env python3
from __future__ import annotations

import hashlib

REVIEW_TYPES = {
    "requirement-quality", "ambiguity", "contradiction", "Design-fidelity",
    "Plan-fidelity", "Build-fidelity", "Conformance-interpretation",
    "evidence-sufficiency",
}
AUDIT_OUTCOMES = {"satisfied", "defect", "insufficient", "governance-required"}
ASSURANCE_EVIDENCE_SURFACES = {
    "github-issue-history",
    "github-pull-request-history",
    "github-review-history",
    "github-check-history",
    "github-development-links",
    "github-merge-history",
    "github-issue-closure-history",
}

class AssuranceError(ValueError):
    pass


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _valid_actor(value):
    if not isinstance(value, dict):
        return False
    actor_id = value.get("id")
    return (
        not isinstance(actor_id, bool)
        and isinstance(actor_id, int)
        and actor_id > 0
        and ("login" not in value or _nonempty(value.get("login")))
    )


def _exact_sha(value):
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(ch in "0123456789abcdefABCDEF" for ch in value)
    )


def triggered_obligation_ids(correspondence_records, subject_requirement_ids):
    subject_ids = set(subject_requirement_ids)
    out = []
    for record in correspondence_records:
        if record.get("requirement_id") in subject_ids and record.get("applicability") == "required":
            out.extend(record.get("obligation_ids", []))
    return out


def validate_review_context(record):
    required = {
        "schema_version", "record_type", "context_id", "authorizing_authority_id",
        "review_obligation_id", "review_type", "reviewed_subject", "evidence",
        "material_exclusions",
    }
    if not isinstance(record, dict) or set(record) != required:
        raise AssuranceError("Assurance review context fields are not canonical")
    if record.get("schema_version") != "1" or record.get("record_type") != "assurance-review-context":
        raise AssuranceError("invalid Assurance review context envelope")
    for key in ("context_id", "authorizing_authority_id", "review_obligation_id"):
        if not _nonempty(record.get(key)):
            raise AssuranceError(f"{key} must be non-empty")
    if record.get("review_type") not in REVIEW_TYPES:
        raise AssuranceError("invalid Assurance review_type")
    subject = record.get("reviewed_subject")
    if not isinstance(subject, dict) or not subject:
        raise AssuranceError("reviewed_subject must be non-empty")
    if subject.get("authority_id") == record["authorizing_authority_id"]:
        raise AssuranceError("review subject cannot authorize its own review")
    if not isinstance(record.get("evidence"), list):
        raise AssuranceError("evidence must be a list")
    if not isinstance(record.get("material_exclusions"), list):
        raise AssuranceError("material_exclusions must be a list")
    issue_number = subject.get("issue_number")
    if isinstance(issue_number, bool) or not isinstance(issue_number, int) or issue_number < 1:
        raise AssuranceError("reviewed subject requires positive issue_number")
    pr_number = subject.get("pull_request_number")
    if pr_number is not None and (isinstance(pr_number, bool) or not isinstance(pr_number, int) or pr_number < 1):
        raise AssuranceError("pull_request_number must be positive when present")
    candidate_sha = subject.get("candidate_sha")
    if candidate_sha is not None and not _exact_sha(candidate_sha):
        raise AssuranceError("candidate_sha must be exact when present")
    return record


def instantiate_review_contexts(
    work_id,
    subject_requirement_ids,
    correspondence_records,
    obligation_records,
    authorizing_authority_id,
    review_type_by_obligation,
    evidence,
    issue_number,
    pull_request_number=None,
    candidate_sha=None,
):
    if not _nonempty(work_id) or not _nonempty(authorizing_authority_id):
        raise AssuranceError("work_id and authorizing_authority_id must be non-empty")
    if not isinstance(review_type_by_obligation, dict) or not isinstance(evidence, list):
        raise AssuranceError("review mapping/evidence invalid")
    if isinstance(issue_number, bool) or not isinstance(issue_number, int) or issue_number < 1:
        raise AssuranceError("issue_number must be positive")
    obligation_by_id = {
        item.get("obligation_id"): item
        for item in obligation_records
        if isinstance(item, dict) and _nonempty(item.get("obligation_id"))
    }
    triggered = triggered_obligation_ids(correspondence_records, subject_requirement_ids)
    contexts = []
    for obligation_id in triggered:
        obligation = obligation_by_id.get(obligation_id)
        if obligation is None:
            raise AssuranceError(f"triggered obligation does not resolve: {obligation_id}")
        review_type = review_type_by_obligation.get(obligation_id)
        if review_type not in REVIEW_TYPES:
            raise AssuranceError(f"triggered obligation lacks review type: {obligation_id}")
        digest = hashlib.sha256(f"{work_id}\0{obligation_id}".encode()).hexdigest()[:24]
        subject = {
            "work_id": work_id,
            "requirement_id": obligation.get("requirement_id"),
            "issue_number": issue_number,
        }
        if pull_request_number is not None:
            subject["pull_request_number"] = pull_request_number
        if candidate_sha is not None:
            if not _exact_sha(candidate_sha):
                raise AssuranceError("candidate_sha must be exact")
            subject["candidate_sha"] = candidate_sha.lower()
        contexts.append(validate_review_context({
            "schema_version": "1",
            "record_type": "assurance-review-context",
            "context_id": f"FS0-AUDIT-{digest}",
            "authorizing_authority_id": authorizing_authority_id,
            "review_obligation_id": obligation_id,
            "review_type": review_type,
            "reviewed_subject": subject,
            "evidence": list(evidence),
            "material_exclusions": [],
        }))
    return contexts


def candidate_merge_disposition(required_obligation_ids, merge_event, authorized_actor, candidate_sha):
    if not _valid_actor(authorized_actor) or not _exact_sha(candidate_sha):
        raise AssuranceError("candidate Assurance identity is invalid")
    if not isinstance(merge_event, dict) or merge_event.get("merged") is not True:
        raise AssuranceError("candidate Assurance requires actual merge")
    actor = merge_event.get("actor")
    if not _valid_actor(actor) or actor.get("id") != authorized_actor.get("id"):
        raise AssuranceError("merge actor is not authorized")
    if str(merge_event.get("head_sha", "")).lower() != candidate_sha.lower():
        raise AssuranceError("merge did not accept reviewed candidate head")
    return {
        "status": "satisfied",
        "basis": "authorized-pr-merge",
        "candidate_sha": candidate_sha.lower(),
        "required_obligation_ids": list(required_obligation_ids),
    }


def issue_close_disposition(required_obligation_ids, issue, authorized_actor, accepted_prs, development_prs):
    if not _valid_actor(authorized_actor):
        raise AssuranceError("authorized actor invalid")
    if not isinstance(issue, dict) or issue.get("state") != "closed":
        raise AssuranceError("completed-work Assurance requires closed issue")
    closed_by = issue.get("closed_by")
    if not _valid_actor(closed_by) or closed_by.get("id") != authorized_actor.get("id"):
        raise AssuranceError("issue close actor is not authorized")
    accepted = set(accepted_prs)
    development = set(development_prs)
    if not accepted or not accepted <= development:
        raise AssuranceError("accepted PRs must be Development-linked")
    return {
        "status": "satisfied",
        "basis": "authorized-issue-close",
        "required_obligation_ids": list(required_obligation_ids),
        "development_pull_request_numbers": sorted(development),
    }
