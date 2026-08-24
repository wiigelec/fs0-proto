#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MARKER = "repo-spec-acceptance:v1"
RECEIPT_REF_PREFIX = "refs/tags/fs0-acceptance/"
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
REQUIRED_FIELDS = {
    "schema_version",
    "record_type",
    "acceptance_id",
    "stage",
    "work_id",
    "candidate_id",
    "disposition",
    "actor",
    "evidence",
    "decision_timestamp",
}


class AcceptanceError(ValueError):
    pass


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _valid_actor(value):
    if not isinstance(value, dict):
        return False
    actor_id = value.get("id")
    if isinstance(actor_id, bool) or not isinstance(actor_id, int) or actor_id < 1:
        return False
    if "login" in value and not _nonempty(value.get("login")):
        return False
    return True


def _github_comment_has_identity(comment):
    if not isinstance(comment, dict):
        return False
    user = comment.get("user")
    return (
        isinstance(user, dict)
        and isinstance(user.get("id"), int)
        and user.get("id") > 0
        and _nonempty(user.get("login"))
    )


def _github_actor_matches_comment(comment, actor):
    # Synthetic repository-local Conformance callers may omit transport metadata.
    # Production GitHub retrieval below admits only comments with id + login.
    if not isinstance(comment, dict):
        return False
    user = comment.get("user")
    if user is None:
        return True
    if not _github_comment_has_identity(comment):
        return False

    user_id = user["id"]

    # Numeric GitHub user ID is the trust key. Login, when present, is display
    # metadata and may change without retroactively invalidating acceptance.
    if not _valid_actor(actor):
        return False
    return actor["id"] == user_id


def _valid_timestamp(value):
    if not _nonempty(value):
        return False
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return False
    return parsed.utcoffset() is not None


def _json_fence_objects(body):
    if not isinstance(body, str):
        return []
    objects = []
    for match in re.finditer(r"```(?:json)?\n(.*?)\n```", body, re.DOTALL):
        try:
            value = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            objects.append(value)
    return objects


def _authorized_actor(issue_body, record_type):
    if record_type == "governance-acceptance":
        path = ("bounded_authorization", "acceptance_actor")
    elif record_type == "bootstrap-acceptance":
        path = ("bootstrap_authorization", "acceptance_actor")
    else:
        return None

    values = []
    for obj in _json_fence_objects(issue_body):
        node = obj
        for key in path:
            if not isinstance(node, dict) or key not in node:
                node = None
                break
            node = node[key]
        if node is not None:
            values.append(node)

    if len(values) != 1 or not _valid_actor(values[0]):
        return None
    return values[0]


def _has_bootstrap_evidence(evidence):
    if not isinstance(evidence, list):
        return False
    labels = set()
    for item in evidence:
        if isinstance(item, str):
            labels.add(item.strip().lower())
        elif isinstance(item, dict):
            for key in ("type", "kind", "evidence_type", "class", "name"):
                value = item.get(key)
                if isinstance(value, str):
                    labels.add(value.strip().lower())
    has_verification = any("verification" in value for value in labels)
    has_audit = any(
        "semantic-audit" in value or "semantic_audit" in value or "semantic audit" in value
        for value in labels
    )
    return has_verification and has_audit


def parse_acceptance_comment(body):
    if not isinstance(body, str) or MARKER not in body:
        return None
    if body.count(MARKER) != 1:
        raise AcceptanceError("acceptance marker must occur exactly once")

    tail = body.split(MARKER, 1)[1]
    if not tail.startswith("\n"):
        raise AcceptanceError("acceptance JSON fence must immediately follow marker")

    lines = tail[1:].splitlines()
    if not lines or lines[0] not in {"```", "```json"}:
        raise AcceptanceError("acceptance marker must be followed by one JSON fence")

    try:
        close_index = lines.index("```", 1)
    except ValueError:
        raise AcceptanceError("acceptance JSON fence is not closed")

    if any(line.startswith("```") for line in lines[close_index + 1:]):
        raise AcceptanceError("acceptance comment contains more than one fenced block")

    payload_text = "\n".join(lines[1:close_index])
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise AcceptanceError(f"acceptance payload is invalid JSON: {exc}")

    if not isinstance(payload, dict):
        raise AcceptanceError("acceptance payload must be a JSON object")

    missing = sorted(REQUIRED_FIELDS - set(payload))
    if missing:
        raise AcceptanceError(f"acceptance payload missing fields: {missing}")

    if payload.get("schema_version") != "1":
        raise AcceptanceError("schema_version must be 1")

    record_type = payload.get("record_type")
    stage = payload.get("stage")
    if record_type == "governance-acceptance":
        if stage not in {"design", "plan", "build"}:
            raise AcceptanceError("governance acceptance stage must be design|plan|build")
    elif record_type == "bootstrap-acceptance":
        if stage != "bootstrap":
            raise AcceptanceError("bootstrap acceptance stage must be bootstrap")
    else:
        raise AcceptanceError("unknown acceptance record_type")

    if payload.get("disposition") not in {"accepted", "rejected"}:
        raise AcceptanceError("disposition must be accepted|rejected")

    for key in ("acceptance_id", "work_id"):
        if not _nonempty(payload.get(key)):
            raise AcceptanceError(f"{key} must be a non-empty string")

    candidate_id = payload.get("candidate_id")
    if not isinstance(candidate_id, str) or not SHA_RE.fullmatch(candidate_id):
        raise AcceptanceError("candidate_id must be an exact 40-hex Git commit SHA")
    payload["candidate_id"] = candidate_id.lower()

    if not _valid_actor(payload.get("actor")):
        raise AcceptanceError("actor must provide attributable identity")
    if not isinstance(payload.get("evidence"), list):
        raise AcceptanceError("evidence must be a machine-readable collection")
    if not _valid_timestamp(payload.get("decision_timestamp")):
        raise AcceptanceError("decision_timestamp must be an unambiguous ISO-8601 timestamp")

    has_resulting = "resulting_accepted_state" in payload
    resulting = payload.get("resulting_accepted_state")
    if has_resulting:
        if not isinstance(resulting, str) or not SHA_RE.fullmatch(resulting):
            raise AcceptanceError(
                "resulting_accepted_state must be an exact 40-hex Git commit SHA"
            )
        payload["resulting_accepted_state"] = resulting.lower()
        resulting = payload["resulting_accepted_state"]

    accepted = payload["disposition"] == "accepted"
    state_producing = (
        record_type == "bootstrap-acceptance"
        or (record_type == "governance-acceptance" and stage == "build")
    )
    must_have_resulting = accepted and state_producing

    if must_have_resulting:
        if not has_resulting:
            raise AcceptanceError(
                "accepted bootstrap/build record requires resulting_accepted_state"
            )
        if resulting != payload["candidate_id"]:
            raise AcceptanceError("resulting_accepted_state must equal candidate_id")
    elif has_resulting:
        raise AcceptanceError(
            "resulting_accepted_state must be absent unless bootstrap/build is accepted"
        )

    if record_type == "bootstrap-acceptance" and not _has_bootstrap_evidence(payload["evidence"]):
        raise AcceptanceError(
            "bootstrap evidence must identify verification and semantic-audit results"
        )

    return payload



def governed_work_from_issue_body(body):
    matches = [
        obj
        for obj in _json_fence_objects(body)
        if obj.get("record_type") == "governed-work"
    ]
    if len(matches) != 1:
        raise AcceptanceError(
            "issue must expose exactly one governed-work JSON record"
        )
    return matches[0]


def governed_pr_candidate_from_body(body):
    matches = [obj for obj in _json_fence_objects(body) if obj.get("record_type") == "governed-pr-candidate"]
    if len(matches) != 1:
        raise AcceptanceError("pull request must expose exactly one governed-pr-candidate JSON record")
    candidate = matches[0]
    required = {"schema_version","record_type","work_id","issue_number","head_sha","accepted_repository_predecessor","base_ref"}
    if set(candidate) != required:
        raise AcceptanceError("governed PR candidate fields are not canonical")
    if candidate.get("schema_version") != "1" or not _nonempty(candidate.get("work_id")):
        raise AcceptanceError("invalid governed PR candidate identity")
    issue_number = candidate.get("issue_number")
    if isinstance(issue_number, bool) or not isinstance(issue_number, int) or issue_number < 1:
        raise AcceptanceError("governed PR candidate issue_number must be positive")
    for key in ("head_sha", "accepted_repository_predecessor"):
        value = candidate.get(key)
        if not isinstance(value, str) or not SHA_RE.fullmatch(value):
            raise AcceptanceError(f"governed PR candidate {key} must be an exact Git SHA")
        candidate[key] = value.lower()
    if candidate.get("base_ref") != "refs/heads/main":
        raise AcceptanceError("governed PR candidate must target refs/heads/main")
    return candidate


def _gh_json(endpoint):
    if shutil.which("gh") is None:
        raise RuntimeError(
            "GitHub CLI (gh) is required for remote Governance and accepted-state resolution"
        )
    proc = _run(["gh", "api", endpoint])
    return json.loads(proc.stdout)


def _github_file_json(repo, path, revision):
    value = _gh_object(f"repos/{repo}/contents/{path}?ref={revision}")
    if value.get("encoding") != "base64" or not isinstance(value.get("content"), str):
        raise RuntimeError(f"GitHub content is not base64 file data: {path}")
    import base64
    raw = base64.b64decode(value["content"].replace("\n", "")).decode("utf-8")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise RuntimeError(f"GitHub JSON file is not an object: {path}")
    return parsed


def _github_json_directory(repo, path, revision):
    value = _gh_json(f"repos/{repo}/contents/{path}?ref={revision}")
    if not isinstance(value, list):
        raise RuntimeError(f"GitHub directory result is not a list: {path}")
    records = []
    for item in value:
        if not isinstance(item, dict) or item.get("type") != "file":
            continue
        name = item.get("name")
        if not isinstance(name, str) or not name.endswith(".json"):
            continue
        records.append(_github_file_json(repo, item["path"], revision))
    return records


def _iso_utc(value):
    if not _nonempty(value):
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.utcoffset() is None:
        return None
    return parsed

def github_candidate_conformance(repo, candidate_sha, merged_at):
    if not isinstance(candidate_sha, str) or not SHA_RE.fullmatch(candidate_sha):
        return {"status": "fail", "defects": ["candidate SHA is not exact"]}
    candidate_sha = candidate_sha.lower()
    merge_time = _iso_utc(merged_at)
    if merge_time is None:
        return {"status": "fail", "candidate_sha": candidate_sha, "defects": ["merge timestamp is not an unambiguous ISO-8601 time"]}
    value = _gh_json(f"repos/{repo}/actions/runs?head_sha={candidate_sha}&event=pull_request&status=completed&per_page=100")
    runs = value.get("workflow_runs") if isinstance(value, dict) else None
    if not isinstance(runs, list):
        return {"status": "fail", "defects": ["GitHub Actions run list is unavailable"]}
    matching = []
    post_merge_successes = []
    for run in runs:
        if not (isinstance(run, dict) and run.get("name") == "FS0 Conformance" and run.get("event") == "pull_request" and str(run.get("head_sha", "")).lower() == candidate_sha and str(run.get("path", "")).endswith(".github/workflows/fs0-conformance.yml")):
            continue
        completed_at = _iso_utc(run.get("updated_at") or run.get("run_started_at"))
        if completed_at is None:
            continue
        if completed_at <= merge_time:
            matching.append((completed_at, run))
        elif run.get("conclusion") == "success":
            post_merge_successes.append((completed_at, run))
    if not matching:
        defects = ["exact candidate lacks completed pre-merge FS0 Conformance pull-request run"]
        if post_merge_successes:
            defects.append("successful exact-candidate Conformance exists only after merge and cannot retroactively establish eligibility")
        return {"status": "fail", "candidate_sha": candidate_sha, "merge_timestamp": merged_at, "defects": defects}
    matching.sort(key=lambda item: (item[0], item[1].get("run_number", 0), item[1].get("run_attempt", 0), item[1].get("id", 0)))
    completed_at, latest = matching[-1]
    passed = latest.get("conclusion") == "success"
    return {"status": "pass" if passed else "fail", "candidate_sha": candidate_sha, "merge_timestamp": merged_at,
            "workflow_run_id": latest.get("id"), "workflow_run_url": latest.get("html_url"),
            "completed_at": completed_at.isoformat(), "conclusion": latest.get("conclusion"),
            "defects": [] if passed else ["latest exact-candidate Conformance completed before merge is not successful"]}


def github_candidate_assurance(repo, candidate_sha, work, merged_at=None):
    required = work.get("required_assurance_obligation_ids")
    if not isinstance(required, list) or any(not _nonempty(x) for x in required):
        return {"status": "fail", "defects": ["governed work lacks required_assurance_obligation_ids"]}
    if len(required) != len(set(required)):
        return {"status": "fail", "defects": ["required Assurance obligation IDs are duplicated"]}
    try:
        binding = github_candidate_binding(repo, candidate_sha, "governed-candidate-binding")
        pin, pin_sha = github_repo_pin(repo, candidate_sha)
    except Exception as exc:
        return {"status": "fail", "candidate_sha": candidate_sha, "defects": [str(exc)]}
    if binding["governed_work"] != work:
        return {"status": "fail", "candidate_sha": candidate_sha, "defects": ["candidate work snapshot mismatch"]}
    if not required:
        return {
            "status": "pass", "candidate_sha": candidate_sha.lower(), "repo_pin_sha": pin_sha,
            "required_obligation_ids": [], "cases": [], "defects": [],
        }
    cases, findings, defects = github_issue_assurance_records(
        repo, binding["issue_number"], merged_at
    )
    case_results = []
    for obligation_id in required:
        matching = [
            case for case in cases
            if case.get("review_obligation_id") == obligation_id
            and isinstance(case.get("reviewed_subject"), dict)
            and case["reviewed_subject"].get("work_id") == work.get("work_id")
            and str(case["reviewed_subject"].get("candidate_sha", "")).lower() == candidate_sha.lower()
            and str(case["reviewed_subject"].get("repo_pin_sha", "")).lower() == pin_sha
        ]
        if len(matching) != 1:
            defects.append(
                f"{obligation_id}: expected exactly one exact-head/repo-pin Assurance case, found {len(matching)}"
            )
            continue
        case = matching[0]
        case_id = case.get("case_id")
        related = [
            finding for finding in findings
            if finding.get("case_id") == case_id
        ]
        seqs = [item.get("sequence") for item in related]
        if (
            not related
            or any(isinstance(seq, bool) or not isinstance(seq, int) or seq < 1 for seq in seqs)
            or len(seqs) != len(set(seqs))
        ):
            defects.append(f"{obligation_id}: Assurance findings are missing or have invalid sequence")
            continue
        latest = max(related, key=lambda item: item["sequence"])
        if latest.get("status") != "satisfied":
            defects.append(f"{obligation_id}: latest Assurance finding is not satisfied")
            continue
        case_results.append({
            "obligation_id": obligation_id,
            "case_id": case_id,
            "finding_id": latest.get("finding_id"),
            "finding_sequence": latest.get("sequence"),
        })
    return {
        "status": "pass" if not defects else "fail",
        "candidate_sha": candidate_sha.lower(),
        "repo_pin_sha": pin_sha,
        "required_obligation_ids": list(required),
        "cases": case_results,
        "defects": defects,
    }


def github_candidate_assurance_from_merge(work, merged_by):
    required = work.get("required_assurance_obligation_ids")
    if not isinstance(required, list) or any(not _nonempty(x) for x in required) or len(required) != len(set(required)):
        return {"status": "fail", "defects": ["governed work lacks valid Assurance obligation set"]}
    auth = work.get("bounded_authorization")
    actor = auth.get("acceptance_actor") if isinstance(auth, dict) else None
    if not _valid_actor(actor) or not isinstance(merged_by, dict) or merged_by.get("id") != actor.get("id"):
        return {"status": "fail", "required_obligation_ids": list(required), "defects": ["candidate Assurance requires authorized merge"]}
    return {"status": "pass", "basis": "authorized-pr-merge", "required_obligation_ids": list(required), "defects": []}

def github_candidate_eligibility(repo, candidate_sha, work, merged_at):
    conformance = github_candidate_conformance(repo, candidate_sha, merged_at)
    return {
        "status": "pass" if conformance.get("status") == "pass" else "fail",
        "candidate_sha": candidate_sha.lower() if isinstance(candidate_sha, str) else candidate_sha,
        "merge_timestamp": merged_at,
        "conformance": conformance,
        "assurance": {"status": "satisfied-by-authorized-merge", "required_obligation_ids": list(work.get("required_assurance_obligation_ids", []))},
        "defects": list(conformance.get("defects", [])),
    }

def resolve_governance_work_acceptance(issue_body, pull_requests, expected_stage, expected_work_id):
    if expected_stage not in {"design", "plan", "build"} or not _nonempty(expected_work_id):
        raise AcceptanceError("invalid requested governed-work acceptance identity")
    fallback_work = None
    try:
        fallback_work = issue_body if isinstance(issue_body, dict) and issue_body.get("record_type") == "governed-work" else governed_work_from_issue_body(issue_body)
    except Exception:
        pass
    matches, defects = [], []
    for pr in pull_requests:
        if not isinstance(pr, dict):
            continue
        bound = pr.get("_fs0_governed_binding")
        if isinstance(bound, dict):
            try:
                bound = validate_governed_candidate_binding(bound)
            except AcceptanceError as exc:
                defects.append({"pull_request_number": pr.get("number"), "error": str(exc)})
                continue
            work = bound["governed_work"]
        elif isinstance(pr.get("_fs0_work"), dict):
            work = pr["_fs0_work"]
        elif "_fs0_eligibility" in pr and fallback_work is not None:
            work = fallback_work
            bound = None
        else:
            defects.append({"pull_request_number": pr.get("number"), "error": "merged PR lacks immutable governed candidate binding"})
            continue
        if work.get("stage") != expected_stage or work.get("work_id") != expected_work_id:
            continue
        actor = work.get("bounded_authorization", {}).get("acceptance_actor")
        required_assurance = work.get("required_assurance_obligation_ids")
        if not _valid_actor(actor) or not isinstance(required_assurance, list):
            defects.append({"pull_request_number": pr.get("number"), "error": "bound authorization/Assurance obligations invalid"})
            continue
        head = pr.get("head")
        head_sha = str(head.get("sha", "")).lower() if isinstance(head, dict) else ""
        try:
            candidate = pr.get("_fs0_candidate")
            if not isinstance(candidate, dict):
                candidate = _candidate_from_governed_binding(bound, head_sha) if isinstance(bound, dict) else governed_pr_candidate_from_body(pr.get("body"))
        except AcceptanceError:
            continue
        number = pr.get("number")
        merged_at = pr.get("merged_at")
        merged_by = pr.get("merged_by")
        base = pr.get("base")
        resulting = pr.get("merge_commit_sha")
        eligibility = pr.get("_fs0_eligibility")
        valid_merge = (
            isinstance(number, int) and not isinstance(number, bool) and number > 0
            and _nonempty(merged_at)
            and isinstance(merged_by, dict) and merged_by.get("id") == actor.get("id")
            and isinstance(head, dict) and head_sha == candidate["head_sha"]
            and isinstance(base, dict) and base.get("ref") == "main"
            and str(base.get("sha", "")).lower() == candidate["accepted_repository_predecessor"]
            and isinstance(resulting, str) and bool(SHA_RE.fullmatch(resulting))
        )
        valid_conf = (
            isinstance(eligibility, dict) and eligibility.get("status") == "pass"
            and str(eligibility.get("candidate_sha", "")).lower() == candidate["head_sha"]
            and isinstance(eligibility.get("conformance"), dict)
            and eligibility["conformance"].get("status") == "pass"
        )
        if not valid_merge:
            defects.append({"pull_request_number": number, "error": "merged PR does not satisfy candidate/actor/predecessor binding"})
            continue
        if not valid_conf:
            defects.append({"pull_request_number": number, "error": "merged PR lacks passing exact-candidate Conformance"})
            continue
        assurance = github_candidate_assurance_from_merge(work, merged_by)
        if assurance.get("status") != "pass":
            defects.append({"pull_request_number": number, "error": "authorized merge did not establish candidate Assurance"})
            continue
        matches.append({
            "schema_version": "1", "record_type": "governed-pr-acceptance", "status": "accepted",
            "work_id": expected_work_id, "issue_number": candidate["issue_number"], "pull_request_number": number,
            "candidate_head": candidate["head_sha"], "accepted_repository_predecessor": candidate["accepted_repository_predecessor"],
            "resulting_accepted_revision": resulting.lower(),
            "actor": {"id": merged_by.get("id"), "login": merged_by.get("login")}, "merged_at": merged_at,
            "eligibility": {"status": "pass", "candidate_sha": candidate["head_sha"], "conformance": eligibility["conformance"], "assurance": assurance},
        })
    if not matches:
        return {"schema_version": "1", "record_type": "governance-work-acceptance-resolution", "status": "invalid", "stage": expected_stage, "work_id": expected_work_id, "acceptance_records": [], "defects": defects or ["governed work has no exact-conforming authorized merged PR acceptance"]}
    matches.sort(key=lambda x: (x["merged_at"], x["pull_request_number"]))
    return {"schema_version": "1", "record_type": "governance-work-acceptance-resolution", "status": "accepted", "stage": expected_stage, "work_id": expected_work_id, "acceptance_records": [matches[-1]], "superseded_acceptance_count": len(matches) - 1, "defects": []}

def github_pull_requests_for_issue(repo, issue_number):
    if isinstance(issue_number, bool) or not isinstance(issue_number, int) or issue_number < 1:
        raise RuntimeError("issue_number must be a positive integer")
    pulls = _gh_paginated(f"repos/{repo}/pulls?state=closed&per_page=100")
    out = []
    for item in pulls:
        if not isinstance(item, dict):
            continue
        number = item.get("number")
        if isinstance(number, bool) or not isinstance(number, int) or number < 1:
            continue
        detail = _gh_object(f"repos/{repo}/pulls/{number}")
        head = detail.get("head")
        head_sha = str(head.get("sha", "")).lower() if isinstance(head, dict) else ""
        if not SHA_RE.fullmatch(head_sha):
            continue
        try:
            binding = github_candidate_binding(repo, head_sha, "governed-candidate-binding")
        except AcceptanceError:
            continue
        if binding.get("issue_number") != issue_number:
            continue
        work = binding["governed_work"]
        candidate = _candidate_from_governed_binding(binding, head_sha)
        detail["_fs0_governed_binding"] = binding
        detail["_fs0_work"] = work
        detail["_fs0_candidate"] = candidate
        detail["_fs0_eligibility"] = github_candidate_eligibility(repo, head_sha, work, detail.get("merged_at"))
        out.append(detail)
    return out


def github_issues(repo):
    issues = _gh_paginated(f"repos/{repo}/issues?state=all&per_page=100")
    return [
        item
        for item in issues
        if isinstance(item, dict) and "pull_request" not in item
    ]


def github_issue_comments_for(repo, issue_number):
    if (
        isinstance(issue_number, bool)
        or not isinstance(issue_number, int)
        or issue_number < 1
    ):
        raise RuntimeError("issue_number must be a positive integer")

    issue = _gh_object(f"repos/{repo}/issues/{issue_number}")
    if "pull_request" in issue:
        raise RuntimeError("bootstrap provenance anchor must resolve to a GitHub issue")

    comments = _gh_paginated(
        f"repos/{repo}/issues/{issue_number}/comments?per_page=100"
    )
    out = []
    for item in comments:
        if not _github_comment_has_identity(item):
            continue
        enriched = dict(item)
        enriched["issue_body"] = issue.get("body")
        enriched["issue_url"] = issue.get("url")
        enriched["issue_number"] = issue.get("number", issue_number)
        out.append(enriched)
    return out


def bootstrap_provenance_issue_number(state):
    if not isinstance(state, dict):
        raise RuntimeError("bootstrap state must be a JSON object")
    value = state.get("bootstrap_provenance_issue")
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise RuntimeError(
            "initial accepted-state resolution requires bootstrap_provenance_issue "
            "to name one positive GitHub issue number"
        )
    return value


def committed_bootstrap_state(root, revision):
    if not isinstance(revision, str) or not SHA_RE.fullmatch(revision):
        raise RuntimeError("bootstrap-state revision must be an exact Git commit SHA")
    proc = _run(["git", "show", f"{revision}:repo/state/bootstrap.json"])
    try:
        state = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"committed bootstrap state is invalid JSON: {exc}")
    if (
        not isinstance(state, dict)
        or state.get("schema_version") != "1"
        or state.get("record_type") != "bootstrap-state"
    ):
        raise RuntimeError("committed bootstrap state has invalid envelope")
    return state


def bootstrap_acceptance_comments(root, repo, revision):
    state = committed_bootstrap_state(root, revision)
    issue_number = bootstrap_provenance_issue_number(state)
    return issue_number, github_issue_comments_for(repo, issue_number)

def acceptance_receipt_tag_name(candidate):
    if not isinstance(candidate, str) or not SHA_RE.fullmatch(candidate):
        raise AcceptanceError("receipt candidate_id must be an exact 40-hex Git commit SHA")
    return "fs0-acceptance/" + candidate.lower()


def acceptance_receipt_ref(candidate):
    return "refs/tags/" + acceptance_receipt_tag_name(candidate)


def _positive_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def acceptance_receipt_payload(candidate, acceptance_item):
    candidate = acceptance_receipt_tag_name(candidate).split("/", 1)[1]
    if not isinstance(acceptance_item, dict):
        raise AcceptanceError("acceptance receipt source must be a record wrapper")
    record = acceptance_item.get("record")
    if not isinstance(record, dict):
        raise AcceptanceError("acceptance receipt source lacks acceptance record")

    body = MARKER + "\n```json\n" + json.dumps(record) + "\n```\n"
    record = parse_acceptance_comment(body)
    state_producing = (
        record["record_type"] == "bootstrap-acceptance"
        or (
            record["record_type"] == "governance-acceptance"
            and record["stage"] == "build"
        )
    )
    if (
        not state_producing
        or record["disposition"] != "accepted"
        or record["candidate_id"] != candidate
        or record.get("resulting_accepted_state") != candidate
    ):
        raise AcceptanceError("receipt source is not the accepted state-producing record")

    authorized_actor = acceptance_item.get("authorized_actor")
    if authorized_actor != record["actor"] or not _valid_actor(authorized_actor):
        raise AcceptanceError("receipt authorization actor does not match acceptance actor")

    github_user_id = acceptance_item.get("github_user_id")
    if not _positive_int(github_user_id) or github_user_id != record["actor"]["id"]:
        raise AcceptanceError("receipt GitHub user id does not match acceptance actor")

    issue_number = acceptance_item.get("issue_number")
    comment_id = acceptance_item.get("comment_id")
    issue_url = acceptance_item.get("issue_url")
    comment_url = acceptance_item.get("comment_url")
    if not _positive_int(issue_number) or not _positive_int(comment_id):
        raise AcceptanceError("receipt provenance requires positive issue/comment ids")
    if not _nonempty(issue_url) or not _nonempty(comment_url):
        raise AcceptanceError("receipt provenance requires issue/comment URLs")

    return {
        "schema_version": "1",
        "record_type": "acceptance-receipt",
        "candidate_id": candidate,
        "acceptance_id": record["acceptance_id"],
        "acceptance_record": record,
        "authorization_actor": authorized_actor,
        "github_user_id": github_user_id,
        "github_provenance": {
            "issue_number": issue_number,
            "issue_url": issue_url,
            "comment_id": comment_id,
            "comment_url": comment_url,
        },
    }


def validate_acceptance_receipt_payload(candidate, payload):
    candidate = acceptance_receipt_tag_name(candidate).split("/", 1)[1]
    if not isinstance(payload, dict):
        raise AcceptanceError("acceptance receipt must be a JSON object")
    expected_fields = {
        "schema_version",
        "record_type",
        "candidate_id",
        "acceptance_id",
        "acceptance_record",
        "authorization_actor",
        "github_user_id",
        "github_provenance",
    }
    if set(payload) != expected_fields:
        raise AcceptanceError("acceptance receipt fields are not canonical")
    if payload.get("schema_version") != "1" or payload.get("record_type") != "acceptance-receipt":
        raise AcceptanceError("acceptance receipt envelope is invalid")
    if payload.get("candidate_id") != candidate:
        raise AcceptanceError("acceptance receipt candidate does not match accepted revision")

    provenance = payload.get("github_provenance")
    item = {
        "record": payload.get("acceptance_record"),
        "authorized_actor": payload.get("authorization_actor"),
        "github_user_id": payload.get("github_user_id"),
        "issue_number": provenance.get("issue_number") if isinstance(provenance, dict) else None,
        "issue_url": provenance.get("issue_url") if isinstance(provenance, dict) else None,
        "comment_id": provenance.get("comment_id") if isinstance(provenance, dict) else None,
        "comment_url": provenance.get("comment_url") if isinstance(provenance, dict) else None,
    }
    canonical = acceptance_receipt_payload(candidate, item)
    if payload != canonical:
        raise AcceptanceError("acceptance receipt is not the canonical snapshot")
    if payload.get("acceptance_id") != canonical["acceptance_record"]["acceptance_id"]:
        raise AcceptanceError("acceptance receipt acceptance_id mismatch")
    return canonical


def canonical_acceptance_receipt_message(payload):
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"


def _decision_epoch(timestamp):
    text = timestamp.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.utcoffset() is None:
        raise AcceptanceError("receipt decision timestamp must be timezone-aware")
    return int(parsed.timestamp())


def acceptance_receipt_tag_text(candidate, payload):
    payload = validate_acceptance_receipt_payload(candidate, payload)
    candidate = payload["candidate_id"]
    tag_name = acceptance_receipt_tag_name(candidate)
    epoch = _decision_epoch(payload["acceptance_record"]["decision_timestamp"])
    message = canonical_acceptance_receipt_message(payload)
    return (
        f"object {candidate}\n"
        "type commit\n"
        f"tag {tag_name}\n"
        f"tagger FS0 Governance <fs0@invalid> {epoch} +0000\n"
        "\n"
        + message
    )


def acceptance_receipt_object_sha(candidate, payload):
    raw = acceptance_receipt_tag_text(candidate, payload).encode("utf-8")
    header = f"tag {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def remote_acceptance_receipt_sha(candidate):
    ref = acceptance_receipt_ref(candidate)
    proc = _run(["git", "ls-remote", "origin", ref], allowed=(0,))
    text = proc.stdout.strip()
    if not text:
        return None
    fields = text.split()
    if len(fields) != 2 or fields[1] != ref:
        raise RuntimeError("unexpected acceptance-receipt ref resolution")
    if not SHA_RE.fullmatch(fields[0]):
        raise RuntimeError("acceptance-receipt ref does not name a Git object")
    return fields[0].lower()


def github_acceptance_receipt(repo, candidate):
    candidate = acceptance_receipt_tag_name(candidate).split("/", 1)[1]
    observed_sha = remote_acceptance_receipt_sha(candidate)
    if observed_sha is None:
        return {
            "status": "invalid",
            "receipt_ref": acceptance_receipt_ref(candidate),
            "receipt_object_sha": None,
            "payload": None,
            "defects": ["accepted revision lacks immutable acceptance receipt"],
        }

    tag_object = _gh_object(f"repos/{repo}/git/tags/{observed_sha}")

    defects = []
    target = tag_object.get("object")
    if (
        not isinstance(target, dict)
        or target.get("type") != "commit"
        or str(target.get("sha", "")).lower() != candidate
    ):
        defects.append("acceptance receipt tag does not target accepted revision")
    if tag_object.get("tag") != acceptance_receipt_tag_name(candidate):
        defects.append("acceptance receipt tag name is not canonical")

    try:
        payload = json.loads(tag_object.get("message"))
        payload = validate_acceptance_receipt_payload(candidate, payload)
        expected_sha = acceptance_receipt_object_sha(candidate, payload)
        if expected_sha != observed_sha:
            defects.append("acceptance receipt Git object hash does not match canonical receipt")
    except (TypeError, json.JSONDecodeError, AcceptanceError) as exc:
        payload = None
        defects.append(str(exc))

    return {
        "status": "valid" if not defects else "invalid",
        "receipt_ref": acceptance_receipt_ref(candidate),
        "receipt_object_sha": observed_sha,
        "payload": payload,
        "defects": defects,
    }


def resolve_published_state(repo, accepted_sha):
    if accepted_sha is None:
        return resolve_accepted_state(None, [])
    if not isinstance(accepted_sha, str) or not SHA_RE.fullmatch(accepted_sha):
        return resolve_accepted_state(accepted_sha, [])

    receipt = github_acceptance_receipt(repo, accepted_sha.lower())
    if receipt.get("status") != "valid":
        return {
            "schema_version": "1",
            "record_type": "accepted-state-resolution",
            "status": "invalid",
            "accepted_revision": accepted_sha.lower(),
            "acceptance_records": [],
            "acceptance_receipt": receipt,
            "defects": list(receipt.get("defects", [])),
        }

    payload = receipt["payload"]
    record = payload["acceptance_record"]
    return {
        "schema_version": "1",
        "record_type": "accepted-state-resolution",
        "status": "accepted",
        "accepted_revision": accepted_sha.lower(),
        "acceptance_records": [
            {
                "record": record,
                "receipt_snapshot": True,
                "issue_number": payload["github_provenance"]["issue_number"],
                "comment_id": payload["github_provenance"]["comment_id"],
                "issue_url": payload["github_provenance"]["issue_url"],
                "comment_url": payload["github_provenance"]["comment_url"],
            }
        ],
        "acceptance_receipt": receipt,
        "defects": [],
    }


def resolve_accepted_state(accepted_sha, comments):
    if accepted_sha is None:
        return {
            "schema_version": "1",
            "record_type": "accepted-state-resolution",
            "status": "unpublished",
            "accepted_revision": None,
            "acceptance_records": [],
            "defects": [],
        }

    if not isinstance(accepted_sha, str) or not SHA_RE.fullmatch(accepted_sha):
        return {
            "schema_version": "1",
            "record_type": "accepted-state-resolution",
            "status": "invalid",
            "accepted_revision": accepted_sha,
            "acceptance_records": [],
            "defects": ["accepted ref does not resolve to an exact Git commit SHA"],
        }

    accepted_sha = accepted_sha.lower()
    matches = []
    defects = []
    acceptance_ids = set()

    for comment in comments:
        body = comment.get("body") if isinstance(comment, dict) else None
        if not isinstance(body, str) or MARKER not in body:
            continue

        # Repository-wide issue comments are untrusted discovery input. A
        # malformed marker outside the authoritative acceptance path cannot
        # invalidate otherwise valid accepted state.
        try:
            record = parse_acceptance_comment(body)
        except AcceptanceError:
            continue

        authorized_actor = _authorized_actor(
            comment.get("issue_body"),
            record["record_type"],
        )
        if authorized_actor is None:
            continue

        # Bind semantic actor identity to GitHub's authenticated comment author.
        if not _github_actor_matches_comment(comment, authorized_actor):
            continue

        state_producing = (
            record["record_type"] == "bootstrap-acceptance"
            or (
                record["record_type"] == "governance-acceptance"
                and record["stage"] == "build"
            )
        )
        relevant = (
            state_producing
            and record["disposition"] == "accepted"
            and record.get("resulting_accepted_state") == accepted_sha
            and record["candidate_id"] == accepted_sha
        )
        if not relevant:
            continue

        if record["actor"] != authorized_actor:
            defects.append(
                {
                    "comment_id": comment.get("id"),
                    "error": "acceptance actor does not match issue authorization",
                }
            )
            continue

        acceptance_id = record["acceptance_id"]
        if acceptance_id in acceptance_ids:
            defects.append(
                {
                    "comment_id": comment.get("id"),
                    "error": f"duplicate acceptance_id: {acceptance_id}",
                }
            )
            continue
        acceptance_ids.add(acceptance_id)

        comment_user = comment.get("user") if isinstance(comment, dict) else None
        github_user_id = (
            comment_user.get("id")
            if isinstance(comment_user, dict)
            else record["actor"]["id"]
        )
        matches.append(
            {
                "record": record,
                "authorized_actor": authorized_actor,
                "github_user_id": github_user_id,
                "issue_number": comment.get("issue_number"),
                "comment_id": comment.get("id"),
                "issue_url": comment.get("issue_url"),
                "comment_url": comment.get("html_url") or comment.get("url"),
            }
        )

    if defects or len(matches) != 1:
        if len(matches) != 1:
            defects.append(
                "accepted ref must have exactly one matching accepted bootstrap/build acceptance record"
            )
        return {
            "schema_version": "1",
            "record_type": "accepted-state-resolution",
            "status": "invalid",
            "accepted_revision": accepted_sha,
            "acceptance_records": matches,
            "defects": defects,
        }

    return {
        "schema_version": "1",
        "record_type": "accepted-state-resolution",
        "status": "accepted",
        "accepted_revision": accepted_sha,
        "acceptance_records": matches,
        "defects": [],
    }

def bootstrap_authorization_from_issue_body(body):
    matches = [obj for obj in _json_fence_objects(body) if obj.get("record_type") == "bootstrap-authorization"]
    if len(matches) != 1:
        raise AcceptanceError("bootstrap provenance issue must expose exactly one bootstrap-authorization JSON record")
    record = matches[0]
    required = {"schema_version","record_type","acceptance_actor","accepted_repository_predecessor","accepted_ref"}
    if set(record) != required or record.get("schema_version") != "1":
        raise AcceptanceError("bootstrap authorization fields are not canonical")
    if not _valid_actor(record.get("acceptance_actor")):
        raise AcceptanceError("bootstrap authorization requires one valid acceptance_actor")
    predecessor = record.get("accepted_repository_predecessor")
    if not isinstance(predecessor, str) or not SHA_RE.fullmatch(predecessor):
        raise AcceptanceError("bootstrap authorization predecessor must be an exact Git SHA")
    if record.get("accepted_ref") != "refs/heads/main":
        raise AcceptanceError("bootstrap authorization accepted_ref must be refs/heads/main")
    record["accepted_repository_predecessor"] = predecessor.lower()
    return record

def bootstrap_cutover_candidate_from_body(body):
    matches = [obj for obj in _json_fence_objects(body) if obj.get("record_type") == "bootstrap-cutover-candidate"]
    if len(matches) != 1:
        raise AcceptanceError("bootstrap cutover PR must expose exactly one bootstrap-cutover-candidate JSON record")
    record = matches[0]
    required = {"schema_version","record_type","bootstrap_provenance_issue","head_sha","accepted_repository_predecessor","base_ref"}
    if set(record) != required or record.get("schema_version") != "1":
        raise AcceptanceError("bootstrap cutover candidate fields are not canonical")
    issue = record.get("bootstrap_provenance_issue")
    if isinstance(issue, bool) or not isinstance(issue, int) or issue < 1:
        raise AcceptanceError("bootstrap cutover candidate provenance issue must be positive")
    for key in ("head_sha","accepted_repository_predecessor"):
        value = record.get(key)
        if not isinstance(value, str) or not SHA_RE.fullmatch(value):
            raise AcceptanceError(f"bootstrap cutover candidate {key} must be an exact Git SHA")
        record[key] = value.lower()
    if record.get("base_ref") != "refs/heads/main":
        raise AcceptanceError("bootstrap cutover candidate must target refs/heads/main")
    return record

def _candidate_binding_from_message(message, record_type):
    if not isinstance(message, str):
        raise AcceptanceError("candidate commit message is unavailable")
    matches = [obj for obj in _json_fence_objects(message) if obj.get("record_type") == record_type]
    if len(matches) != 1:
        raise AcceptanceError(f"candidate commit must contain exactly one {record_type} JSON binding")
    return matches[0]

def verify_action_candidate_binding(root):
    if os.environ.get("GITHUB_EVENT_NAME") != "pull_request":
        return {"status": "pass", "mode": "not-pull-request", "defects": []}
    repo = os.environ.get("GITHUB_REPOSITORY")
    candidate_sha = os.environ.get("FS0_CANDIDATE_SHA")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not isinstance(repo, str) or not repo or not isinstance(candidate_sha, str) or not SHA_RE.fullmatch(candidate_sha):
        return {"status": "fail", "defects": ["GitHub Actions candidate environment is incomplete"]}
    try:
        event = json.loads(Path(event_path).read_text(encoding="utf-8"))
        pr = event.get("pull_request")
        if not isinstance(pr, dict) or not isinstance(pr.get("base"), dict) or pr["base"].get("ref") != "main":
            raise AcceptanceError("candidate PR does not target main")
        try:
            governed = github_candidate_binding(repo, candidate_sha, "governed-candidate-binding")
        except Exception:
            governed = None
        if governed is not None:
            issue = _gh_object(f"repos/{repo}/issues/{governed['issue_number']}")
            current_work = governed_work_from_issue_body(issue.get("body"))
            if current_work != governed["governed_work"]:
                raise AcceptanceError("governed issue no longer matches candidate snapshot")
            return {"status": "pass", "mode": "governed", "issue_number": governed["issue_number"], "candidate_sha": candidate_sha.lower(), "defects": []}
        bootstrap = github_candidate_binding(repo, candidate_sha, "bootstrap-candidate-binding")
        issue = _gh_object(f"repos/{repo}/issues/{bootstrap['bootstrap_provenance_issue']}")
        auth = bootstrap_authorization_from_issue_body(issue.get("body"))
        if auth["acceptance_actor"].get("id") != bootstrap["acceptance_actor"].get("id"):
            raise AcceptanceError("bootstrap issue actor does not match candidate binding")
        return {"status": "pass", "mode": "bootstrap", "issue_number": bootstrap["bootstrap_provenance_issue"], "candidate_sha": candidate_sha.lower(), "defects": []}
    except Exception as exc:
        return {"status": "fail", "defects": [str(exc)]}

def validate_governed_candidate_binding(binding):
    required = {"schema_version", "record_type", "issue_number", "accepted_repository_predecessor", "base_ref", "governed_work"}
    if not isinstance(binding, dict) or set(binding) != required:
        raise AcceptanceError("governed candidate binding fields are not canonical")
    if binding.get("schema_version") != "1" or binding.get("record_type") != "governed-candidate-binding":
        raise AcceptanceError("governed candidate binding envelope is invalid")
    issue = binding.get("issue_number")
    if isinstance(issue, bool) or not isinstance(issue, int) or issue < 1:
        raise AcceptanceError("governed candidate binding issue_number must be positive")
    predecessor = binding.get("accepted_repository_predecessor")
    if not isinstance(predecessor, str) or not SHA_RE.fullmatch(predecessor):
        raise AcceptanceError("governed candidate binding predecessor must be exact Git SHA")
    if binding.get("base_ref") != "refs/heads/main":
        raise AcceptanceError("governed candidate binding must target refs/heads/main")
    work = binding.get("governed_work")
    if not isinstance(work, dict) or work.get("record_type") != "governed-work":
        raise AcceptanceError("governed candidate binding work identity is invalid")
    auth = work.get("bounded_authorization")
    actor = auth.get("acceptance_actor") if isinstance(auth, dict) else None
    if not _valid_actor(actor):
        raise AcceptanceError("governed candidate binding lacks valid acceptance_actor")
    obligations = work.get("required_assurance_obligation_ids")
    if not isinstance(obligations, list) or len(obligations) != len(set(obligations)):
        raise AcceptanceError("governed candidate binding Assurance obligation set is invalid")
    out = dict(binding)
    out["accepted_repository_predecessor"] = predecessor.lower()
    out["governed_work"] = dict(work)
    return out

def validate_bootstrap_candidate_binding(binding):
    required = {"schema_version", "record_type", "bootstrap_provenance_issue", "acceptance_actor", "accepted_repository_predecessor", "base_ref"}
    if not isinstance(binding, dict) or set(binding) != required:
        raise AcceptanceError("bootstrap candidate binding fields are not canonical")
    if binding.get("schema_version") != "1" or binding.get("record_type") != "bootstrap-candidate-binding":
        raise AcceptanceError("bootstrap candidate binding envelope is invalid")
    issue = binding.get("bootstrap_provenance_issue")
    if isinstance(issue, bool) or not isinstance(issue, int) or issue < 1:
        raise AcceptanceError("bootstrap provenance issue must be positive")
    if not _valid_actor(binding.get("acceptance_actor")):
        raise AcceptanceError("bootstrap candidate binding lacks valid acceptance_actor")
    predecessor = binding.get("accepted_repository_predecessor")
    if not isinstance(predecessor, str) or not SHA_RE.fullmatch(predecessor):
        raise AcceptanceError("bootstrap predecessor must be exact Git SHA")
    if binding.get("base_ref") != "refs/heads/main":
        raise AcceptanceError("bootstrap candidate binding must target refs/heads/main")
    out = dict(binding)
    out["accepted_repository_predecessor"] = predecessor.lower()
    return out

def github_candidate_binding(repo, candidate_sha, record_type):
    if not isinstance(candidate_sha, str) or not SHA_RE.fullmatch(candidate_sha):
        raise AcceptanceError("candidate binding lookup requires exact Git SHA")
    value = _gh_object(f"repos/{repo}/git/commits/{candidate_sha.lower()}")
    record = _candidate_binding_from_message(value.get("message"), record_type)
    if record_type == "governed-candidate-binding":
        return validate_governed_candidate_binding(record)
    if record_type == "bootstrap-candidate-binding":
        return validate_bootstrap_candidate_binding(record)
    raise AcceptanceError("unsupported candidate binding record type")

def _candidate_from_governed_binding(binding, head_sha):
    binding = validate_governed_candidate_binding(binding)
    if not isinstance(head_sha, str) or not SHA_RE.fullmatch(head_sha):
        raise AcceptanceError("governed candidate head must be exact Git SHA")
    work = binding["governed_work"]
    return {
        "schema_version":"1","record_type":"governed-pr-candidate",
        "work_id":work["work_id"],"issue_number":binding["issue_number"],
        "head_sha":head_sha.lower(),
        "accepted_repository_predecessor":binding["accepted_repository_predecessor"],
        "base_ref":"refs/heads/main",
    }

def github_resulting_pull_requests(repo, accepted_sha):
    if not isinstance(accepted_sha, str) or not SHA_RE.fullmatch(accepted_sha):
        raise RuntimeError("accepted revision must be an exact Git SHA")
    accepted_sha = accepted_sha.lower()
    pulls = _gh_paginated(f"repos/{repo}/pulls?state=closed&per_page=100")
    out = []
    for item in pulls:
        number = item.get("number") if isinstance(item, dict) else None
        if isinstance(number, bool) or not isinstance(number, int) or number < 1:
            continue
        detail = _gh_object(f"repos/{repo}/pulls/{number}")
        if str(detail.get("merge_commit_sha", "")).lower() != accepted_sha:
            continue
        head = detail.get("head")
        head_sha = str(head.get("sha", "")).lower() if isinstance(head, dict) else ""
        if SHA_RE.fullmatch(head_sha):
            try:
                detail["_fs0_governed_binding"] = github_candidate_binding(repo, head_sha, "governed-candidate-binding")
            except Exception:
                pass
            try:
                detail["_fs0_bootstrap_binding"] = github_candidate_binding(repo, head_sha, "bootstrap-candidate-binding")
            except Exception:
                pass
        out.append(detail)
    return out

def resolve_bootstrap_merge_acceptance(repo, bootstrap_state, accepted_sha, pull_requests=None, provenance_issue=None):
    if not isinstance(accepted_sha, str) or not SHA_RE.fullmatch(accepted_sha):
        return {"status":"invalid","defects":["accepted revision is not an exact Git SHA"]}
    accepted_sha = accepted_sha.lower()
    if not isinstance(bootstrap_state, dict) or bootstrap_state.get("state") != "cutover":
        return {"status":"invalid","defects":["bootstrap state is not cutover"]}
    issue_number = bootstrap_state.get("bootstrap_provenance_issue")
    if isinstance(issue_number, bool) or not isinstance(issue_number, int) or issue_number < 1:
        return {"status":"invalid","defects":["cutover state lacks bootstrap provenance issue"]}
    pulls = pull_requests if pull_requests is not None else github_resulting_pull_requests(repo, accepted_sha)
    matches, defects = [], []
    for pr in pulls:
        if not isinstance(pr, dict):
            continue
        head = pr.get("head")
        head_sha = str(head.get("sha", "")).lower() if isinstance(head, dict) else ""
        binding = pr.get("_fs0_bootstrap_binding")
        if not isinstance(binding, dict):
            if "_fs0_bootstrap_conformance" in pr:
                try:
                    old_candidate = bootstrap_cutover_candidate_from_body(pr.get("body"))
                    old_auth = bootstrap_authorization_from_issue_body((provenance_issue or {}).get("body"))
                    binding = {
                        "schema_version":"1","record_type":"bootstrap-candidate-binding",
                        "bootstrap_provenance_issue":old_candidate["bootstrap_provenance_issue"],
                        "acceptance_actor":old_auth["acceptance_actor"],
                        "accepted_repository_predecessor":old_candidate["accepted_repository_predecessor"],
                        "base_ref":old_candidate["base_ref"],
                    }
                except Exception:
                    binding = None
            elif SHA_RE.fullmatch(head_sha):
                try:
                    binding = github_candidate_binding(repo, head_sha, "bootstrap-candidate-binding")
                except Exception as exc:
                    defects.append(str(exc))
                    continue
        if not isinstance(binding, dict):
            continue
        try:
            binding = validate_bootstrap_candidate_binding(binding)
        except AcceptanceError as exc:
            defects.append(str(exc))
            continue
        if binding.get("bootstrap_provenance_issue") != issue_number:
            continue
        actor = binding["acceptance_actor"]
        predecessor = binding["accepted_repository_predecessor"]
        number = pr.get("number")
        merged_at = pr.get("merged_at")
        merged_by = pr.get("merged_by")
        base = pr.get("base")
        valid = (
            isinstance(number, int) and not isinstance(number, bool) and number > 0
            and _nonempty(merged_at)
            and isinstance(merged_by, dict) and merged_by.get("id") == actor.get("id")
            and isinstance(head, dict) and bool(SHA_RE.fullmatch(head_sha))
            and isinstance(base, dict) and base.get("ref") == "main"
            and str(base.get("sha", "")).lower() == predecessor
            and str(pr.get("merge_commit_sha", "")).lower() == accepted_sha
        )
        if not valid:
            defects.append({"pull_request_number":number,"error":"bootstrap immutable merge binding invalid"})
            continue
        conformance = pr.get("_fs0_bootstrap_conformance")
        if not isinstance(conformance, dict):
            conformance = github_candidate_conformance(repo, head_sha, merged_at)
        if conformance.get("status") != "pass":
            defects.append({"pull_request_number":number,"error":"bootstrap exact-head Conformance did not pass before merge"})
            continue
        matches.append({
            "schema_version":"1","record_type":"bootstrap-pr-acceptance","status":"accepted",
            "bootstrap_provenance_issue":issue_number,"pull_request_number":number,
            "candidate_head":head_sha,"accepted_repository_predecessor":predecessor,
            "resulting_accepted_revision":accepted_sha,
            "actor":{"id":merged_by.get("id"),"login":merged_by.get("login")},
            "merged_at":merged_at,
            "eligibility":{"status":"pass","mechanical_verification":conformance,"semantic_audit":{"status":"satisfied-by-authorized-merge"}},
        })
    if len(matches) != 1:
        defects.append(f"accepted bootstrap revision must resolve to exactly one eligible designated cutover PR; found {len(matches)}")
        return {"status":"invalid","defects":defects,"acceptance_records":matches}
    return matches[0]

def resolve_governed_resulting_acceptance(repo, accepted_sha, pull_requests=None):
    if not isinstance(accepted_sha, str) or not SHA_RE.fullmatch(accepted_sha):
        return {"status":"invalid","defects":["accepted revision is not an exact Git SHA"]}
    accepted_sha = accepted_sha.lower()
    pulls = pull_requests if pull_requests is not None else github_resulting_pull_requests(repo, accepted_sha)
    matches, defects = [], []
    for pr in pulls:
        if not isinstance(pr, dict):
            continue
        head = pr.get("head")
        head_sha = str(head.get("sha", "")).lower() if isinstance(head, dict) else ""
        binding = pr.get("_fs0_governed_binding")
        if not isinstance(binding, dict):
            if not SHA_RE.fullmatch(head_sha):
                continue
            try:
                binding = github_candidate_binding(repo, head_sha, "governed-candidate-binding")
            except Exception as exc:
                defects.append(str(exc))
                continue
        try:
            binding = validate_governed_candidate_binding(binding)
            work = binding["governed_work"]
            candidate = _candidate_from_governed_binding(binding, head_sha)
            detail = dict(pr)
            detail["_fs0_governed_binding"] = binding
            detail["_fs0_work"] = work
            detail["_fs0_candidate"] = candidate
            if not isinstance(detail.get("_fs0_eligibility"), dict):
                detail["_fs0_eligibility"] = github_candidate_eligibility(repo, head_sha, work, detail.get("merged_at"))
            resolution = resolve_governance_work_acceptance(work, [detail], work["stage"], work["work_id"])
        except Exception as exc:
            defects.append(str(exc))
            continue
        records = resolution.get("acceptance_records", [])
        if resolution.get("status") == "accepted" and len(records) == 1 and records[0].get("resulting_accepted_revision") == accepted_sha:
            matches.append(records[0])
        else:
            defects.extend(resolution.get("defects", []))
    if len(matches) != 1:
        defects.append(f"accepted governed revision must resolve to exactly one eligible authorized merged PR; found {len(matches)}")
        return {"status":"invalid","defects":defects,"acceptance_records":matches}
    return matches[0]

def resolve_remote_main_acceptance(repo, bootstrap_state, accepted_sha, pull_requests=None, provenance_issue=None):
    if not isinstance(bootstrap_state, dict) or bootstrap_state.get("state") != "cutover":
        return resolve_main_revision(bootstrap_state, accepted_sha, None)
    pulls = pull_requests if pull_requests is not None else github_resulting_pull_requests(repo, accepted_sha)
    bootstrap = resolve_bootstrap_merge_acceptance(repo, bootstrap_state, accepted_sha, pulls, provenance_issue)
    if bootstrap.get("status") == "accepted":
        return resolve_main_revision(bootstrap_state, accepted_sha, bootstrap)
    governed = resolve_governed_resulting_acceptance(repo, accepted_sha, pulls)
    if governed.get("status") == "accepted":
        return resolve_main_revision(bootstrap_state, accepted_sha, governed)
    return {"schema_version":"1","record_type":"accepted-state-resolution","status":"invalid",
            "accepted_revision":None,"repository_revision":accepted_sha.lower(),
            "accepted_ref":"refs/heads/main","acceptance_records":[],
            "defects":list(bootstrap.get("defects",[]))+list(governed.get("defects",[]))}

def resolve_main_revision(bootstrap_state, revision, acceptance=None):
    if not isinstance(revision, str) or not SHA_RE.fullmatch(revision):
        return {"schema_version":"1","record_type":"accepted-state-resolution","status":"invalid","accepted_revision":None,"accepted_ref":"refs/heads/main","defects":["main does not resolve to an exact Git commit SHA"]}
    revision = revision.lower()
    if not isinstance(bootstrap_state, dict) or bootstrap_state.get("state") != "cutover":
        return {"schema_version":"1","record_type":"accepted-state-resolution","status":"unaccepted","accepted_revision":None,"repository_revision":revision,"accepted_ref":"refs/heads/main","defects":[]}
    if not (isinstance(acceptance, dict)
            and acceptance.get("record_type") in {"bootstrap-pr-acceptance","governed-pr-acceptance"}
            and acceptance.get("status") == "accepted"
            and acceptance.get("resulting_accepted_revision") == revision
            and _valid_actor(acceptance.get("actor"))):
        return {"schema_version":"1","record_type":"accepted-state-resolution","status":"invalid","accepted_revision":None,"repository_revision":revision,"accepted_ref":"refs/heads/main","acceptance_records":[],"defects":["main revision lacks resolved authorized eligible merge acceptance"]}
    return {"schema_version":"1","record_type":"accepted-state-resolution","status":"accepted","accepted_revision":revision,"repository_revision":revision,"accepted_ref":"refs/heads/main","provenance_resolution":acceptance["record_type"],"acceptance_records":[acceptance],"defects":[]}

def _run(args, allowed=(0,)):
    proc = subprocess.run(args, text=True, capture_output=True)
    if proc.returncode not in allowed:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"{' '.join(args)} failed ({proc.returncode}): {detail}")
    return proc


def repository_root():
    root = Path.cwd().resolve()
    if not (root / ".git").exists():
        raise RuntimeError("repo/scripts/accepted-state must be invoked from repository root")
    return root


def origin_repository(root):
    remote = _run(["git", "remote", "get-url", "origin"]).stdout.strip()
    patterns = (
        r"^https://github\.com/([^/]+/[^/]+?)(?:\.git)?$",
        r"^git@github\.com:([^/]+/[^/]+?)(?:\.git)?$",
        r"^ssh://git@github\.com/([^/]+/[^/]+?)(?:\.git)?$",
    )
    for pattern in patterns:
        match = re.match(pattern, remote)
        if match:
            return match.group(1)
    raise RuntimeError("origin must resolve to a github.com owner/repository")


def accepted_ref(root):
    proc = _run(
        ["git", "ls-remote", "--heads", "origin", "refs/heads/main"],
        allowed=(0,),
    )
    text = proc.stdout.strip()
    if not text:
        return None
    parts = text.split()
    if len(parts) != 2 or parts[1] != "refs/heads/main":
        raise RuntimeError("unexpected accepted-ref resolution")
    return parts[0].lower()


def _gh_paginated(endpoint):
    if shutil.which("gh") is None:
        raise RuntimeError(
            "GitHub CLI (gh) is required for remote Governance and accepted-state resolution"
        )
    proc = _run(["gh", "api", "--paginate", "--slurp", endpoint])
    pages = json.loads(proc.stdout)
    if not isinstance(pages, list):
        raise RuntimeError("GitHub API pagination result is not a list")
    out = []
    for page in pages:
        if isinstance(page, list):
            out.extend(page)
        else:
            raise RuntimeError("GitHub API pagination page is not a list")
    return out


def _gh_object(endpoint):
    if shutil.which("gh") is None:
        raise RuntimeError(
            "GitHub CLI (gh) is required for remote Governance and accepted-state resolution"
        )
    proc = _run(["gh", "api", endpoint])
    value = json.loads(proc.stdout)
    if not isinstance(value, dict):
        raise RuntimeError("GitHub API object result is not an object")
    return value


def github_issue_comments(repo):
    issues = _gh_paginated(f"repos/{repo}/issues?state=all&per_page=100")
    issue_by_url = {
        item.get("url"): item
        for item in issues
        if isinstance(item, dict) and "pull_request" not in item and item.get("url")
    }
    comments = _gh_paginated(f"repos/{repo}/issues/comments?per_page=100")
    out = []
    for item in comments:
        if (
            not isinstance(item, dict)
            or item.get("issue_url") not in issue_by_url
            or not _github_comment_has_identity(item)
        ):
            continue
        enriched = dict(item)
        issue = issue_by_url[item["issue_url"]]
        enriched["issue_body"] = issue.get("body")
        enriched["issue_number"] = issue.get("number")
        out.append(enriched)
    return out



def _gh_graphql(query, variables):
    if shutil.which("gh") is None:
        raise RuntimeError("GitHub CLI (gh) is required for remote Governance resolution")
    args = ["gh", "api", "graphql", "-f", "query=" + query]
    for key, value in variables.items():
        args += ["-F", f"{key}={value}"]
    value = json.loads(_run(args).stdout)
    if not isinstance(value, dict):
        raise RuntimeError("GitHub GraphQL result is not an object")
    return value


def github_issue_development_pull_requests(repo, issue_number):
    if "/" not in repo:
        raise RuntimeError("repository must be owner/name")
    owner, name = repo.split("/", 1)
    query = "query($owner:String!,$name:String!,$number:Int!){repository(owner:$owner,name:$name){issue(number:$number){closedByPullRequestsReferences(first:100,includeClosedPrs:true,userLinkedOnly:true){nodes{number merged mergedAt}}}}}"
    value = _gh_graphql(query, {"owner": owner, "name": name, "number": issue_number})
    issue = value.get("data", {}).get("repository", {}).get("issue")
    nodes = issue.get("closedByPullRequestsReferences", {}).get("nodes") if isinstance(issue, dict) else None
    if not isinstance(nodes, list):
        raise RuntimeError("GitHub Development PR relationship unavailable")
    return sorted({x["number"] for x in nodes if isinstance(x, dict) and isinstance(x.get("number"), int) and x.get("merged") is True})


def github_governed_issue_completion(repo, issue_number):
    issue = _gh_object(f"repos/{repo}/issues/{issue_number}")
    if "pull_request" in issue:
        return {"status": "invalid", "issue_number": issue_number, "defects": ["governed identity resolved to PR"]}
    try:
        work = governed_work_from_issue_body(issue.get("body"))
    except Exception as exc:
        return {"status": "invalid", "issue_number": issue_number, "defects": [str(exc)]}
    actor = work.get("bounded_authorization", {}).get("acceptance_actor")
    if issue.get("state") != "closed":
        return {"status": "open", "work_id": work.get("work_id"), "issue_number": issue_number, "defects": []}
    closed_by = issue.get("closed_by")
    if not _valid_actor(actor) or not isinstance(closed_by, dict) or closed_by.get("id") != actor.get("id"):
        return {"status": "invalid", "work_id": work.get("work_id"), "issue_number": issue_number, "defects": ["governed issue was not closed by authorized actor"]}
    pulls = github_pull_requests_for_issue(repo, issue_number)
    accepted_records = []
    completion_defects = []
    for pr in pulls:
        resolution = resolve_governance_work_acceptance(
            work, [pr], work.get("stage"), work.get("work_id")
        )
        if resolution.get("status") == "accepted":
            accepted_records.extend(resolution.get("acceptance_records", []))
        else:
            completion_defects.extend(resolution.get("defects", []))
    accepted_records.sort(key=lambda x: (x.get("merged_at", ""), x.get("pull_request_number", 0)))
    accepted_numbers = sorted({x.get("pull_request_number") for x in accepted_records if isinstance(x.get("pull_request_number"), int)})
    if not accepted_numbers:
        return {"status": "invalid", "work_id": work.get("work_id"), "issue_number": issue_number, "defects": completion_defects or ["closed issue lacks accepted governed PR"]}
    development_numbers = github_issue_development_pull_requests(repo, issue_number)
    if not set(accepted_numbers) <= set(development_numbers):
        return {"status": "invalid", "work_id": work.get("work_id"), "issue_number": issue_number, "defects": ["accepted PRs are not all manually linked through GitHub Development"]}
    latest = accepted_records[-1]
    return {
        "schema_version": "1", "record_type": "governed-work-completion", "status": "complete",
        "stage": work.get("stage"), "work_id": work.get("work_id"), "issue_number": issue_number,
        "accepted_pull_request_numbers": accepted_numbers, "development_pull_request_numbers": development_numbers,
        "resulting_accepted_revision": latest.get("resulting_accepted_revision"), "closed_at": issue.get("closed_at"),
        "actor": {"id": closed_by.get("id"), "login": closed_by.get("login")},
        "assurance": {"status": "pass", "basis": "authorized-issue-close", "required_obligation_ids": list(work.get("required_assurance_obligation_ids", []))},
        "defects": [],
    }


def main():
    parser = argparse.ArgumentParser(
        prog="repo/scripts/accepted-state",
        description="Resolve canonical FS0 accepted repository state from refs/heads/main.",
    )
    parser.add_argument("--json", action="store_true", help="emit structured JSON")
    parser.add_argument(
        "--verify-action-binding",
        action="store_true",
        help="verify exact PR-head candidate binding and governing issue correspondence",
    )
    parser.add_argument(
        "--issue-completion",
        type=int,
        help="resolve governed issue completion Assurance from GitHub state",
    )
    args = parser.parse_args()
    if args.issue_completion is not None:
        try:
            root = repository_root()
            report = github_governed_issue_completion(origin_repository(root), args.issue_completion)
        except Exception as exc:
            report = {"status": "invalid", "defects": [str(exc)]}
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("FS0 governed work completion: " + report.get("status", "invalid").upper())
            for defect in report.get("defects", []):
                print("Defect: " + str(defect), file=sys.stderr)
        return 0 if report.get("status") == "complete" else 1
    if args.verify_action_binding:
        try:
            report = verify_action_candidate_binding(repository_root())
        except Exception as exc:
            report = {"status": "fail", "defects": [str(exc)]}
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("FS0 candidate binding: " + report.get("status", "fail").upper())
            for defect in report.get("defects", []):
                print("Defect: " + str(defect), file=sys.stderr)
        return 0 if report.get("status") == "pass" else 1
    try:
        root = repository_root()
        sha = accepted_ref(root)
        if sha is None:
            report = {
                "schema_version": "1", "record_type": "accepted-state-resolution",
                "status": "unpublished", "accepted_revision": None,
                "accepted_ref": "refs/heads/main", "defects": [],
            }
        else:
            bootstrap = committed_bootstrap_state(root, sha)
            if bootstrap.get("state") == "cutover":
                report = resolve_remote_main_acceptance(origin_repository(root), bootstrap, sha)
            else:
                report = resolve_main_revision(bootstrap, sha, None)
    except Exception as exc:
        report = {
            "schema_version": "1", "record_type": "accepted-state-resolution",
            "status": "error", "accepted_revision": None,
            "accepted_ref": "refs/heads/main", "defects": [str(exc)],
        }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("FS0 accepted state: " + report["status"].upper())
        if report.get("accepted_revision"):
            print("Revision: " + report["accepted_revision"])
        for defect in report.get("defects", []):
            print("Defect: " + str(defect), file=sys.stderr)
    return 0 if report["status"] == "accepted" else 1



if __name__ == "__main__":
    raise SystemExit(main())
