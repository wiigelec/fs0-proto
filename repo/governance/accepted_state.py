#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import argparse
import json
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


def resolve_governance_work_acceptance(issue_body, comments, expected_stage, expected_work_id):
    if expected_stage not in {"design", "plan", "build"}:
        raise AcceptanceError("expected_stage must be design|plan|build")
    if not _nonempty(expected_work_id):
        raise AcceptanceError("expected_work_id must be non-empty")

    authorized_actor = _authorized_actor(
        issue_body,
        "governance-acceptance",
    )
    if authorized_actor is None:
        return {
            "schema_version": "1",
            "record_type": "governance-work-acceptance-resolution",
            "status": "invalid",
            "stage": expected_stage,
            "work_id": expected_work_id,
            "acceptance_records": [],
            "defects": [
                "issue does not expose exactly one machine-resolvable acceptance_actor"
            ],
        }

    matches = []
    defects = []
    seen_ids = set()

    for comment in comments:
        body = comment.get("body") if isinstance(comment, dict) else None
        if not isinstance(body, str) or MARKER not in body:
            continue
        # Authenticate before parsing or uniqueness checks. Untrusted
        # commenters cannot create either acceptance or a resolution defect.
        if not _github_actor_matches_comment(comment, authorized_actor):
            continue

        try:
            record = parse_acceptance_comment(body)
        except AcceptanceError as exc:
            defects.append({
                "comment_id": comment.get("id") if isinstance(comment, dict) else None,
                "error": str(exc),
            })
            continue

        if (
            record.get("record_type") != "governance-acceptance"
            or record.get("stage") != expected_stage
            or record.get("work_id") != expected_work_id
        ):
            continue

        acceptance_id = record["acceptance_id"]
        if acceptance_id in seen_ids:
            defects.append({
                "comment_id": comment.get("id") if isinstance(comment, dict) else None,
                "error": f"duplicate acceptance_id: {acceptance_id}",
            })
            continue
        seen_ids.add(acceptance_id)

        if record.get("actor") != authorized_actor:
            defects.append({
                "comment_id": comment.get("id") if isinstance(comment, dict) else None,
                "error": "acceptance actor does not match issue authorization",
            })
            continue

        if record.get("disposition") == "accepted":
            matches.append({
                "record": record,
                "comment_id": comment.get("id") if isinstance(comment, dict) else None,
                "comment_url": (
                    comment.get("html_url") or comment.get("url")
                    if isinstance(comment, dict)
                    else None
                ),
            })

    if defects or len(matches) != 1:
        if len(matches) != 1:
            defects.append(
                "governed work must have exactly one matching accepted Governance record"
            )
        return {
            "schema_version": "1",
            "record_type": "governance-work-acceptance-resolution",
            "status": "invalid",
            "stage": expected_stage,
            "work_id": expected_work_id,
            "acceptance_records": matches,
            "defects": defects,
        }

    return {
        "schema_version": "1",
        "record_type": "governance-work-acceptance-resolution",
        "status": "accepted",
        "stage": expected_stage,
        "work_id": expected_work_id,
        "acceptance_records": matches,
        "defects": [],
    }


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
        ["git", "ls-remote", "--heads", "origin", "refs/heads/accepted"],
        allowed=(0,),
    )
    text = proc.stdout.strip()
    if not text:
        return None
    parts = text.split()
    if len(parts) != 2 or parts[1] != "refs/heads/accepted":
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


def main():
    parser = argparse.ArgumentParser(
        prog="repo/scripts/accepted-state",
        description="Resolve canonical FS0 accepted repository state.",
    )
    parser.add_argument("--json", action="store_true", help="emit structured JSON")
    args = parser.parse_args()

    try:
        root = repository_root()
        sha = accepted_ref(root)
        if sha is None:
            report = resolve_accepted_state(None, [])
        else:
            repo = origin_repository(root)
            report = resolve_published_state(repo, sha)
            report["provenance_resolution"] = "immutable-acceptance-receipt"
    except Exception as exc:
        report = {
            "schema_version": "1",
            "record_type": "accepted-state-resolution",
            "status": "error",
            "accepted_revision": None,
            "acceptance_records": [],
            "defects": [str(exc)],
        }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = report["status"].upper()
        print(f"FS0 accepted state: {status}")
        if report.get("accepted_revision"):
            print(f"Revision: {report['accepted_revision']}")
        if report.get("acceptance_records"):
            ids = [
                item["record"]["acceptance_id"]
                for item in report["acceptance_records"]
            ]
            print("Acceptance: " + ", ".join(ids))
        for defect in report.get("defects", []):
            print(f"Defect: {defect}", file=sys.stderr)

    if report["status"] == "accepted":
        return 0
    if report["status"] == "unpublished":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
