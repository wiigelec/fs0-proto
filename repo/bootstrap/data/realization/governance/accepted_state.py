#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MARKER = "repo-spec-acceptance:v1"
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
    return _nonempty(value) or (isinstance(value, dict) and bool(value))


def _valid_timestamp(value):
    if not _nonempty(value):
        return False
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        datetime.fromisoformat(text)
    except ValueError:
        return False
    return True


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

    if len(values) != 1:
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
    parsed = []
    defects = []
    acceptance_ids = set()

    for comment in comments:
        body = comment.get("body") if isinstance(comment, dict) else None
        if not isinstance(body, str) or MARKER not in body:
            continue
        try:
            record = parse_acceptance_comment(body)
        except AcceptanceError as exc:
            defects.append(
                {
                    "comment_id": comment.get("id") if isinstance(comment, dict) else None,
                    "error": str(exc),
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

        authorized_actor = _authorized_actor(comment.get("issue_body"), record["record_type"])
        if authorized_actor is None:
            defects.append(
                {
                    "comment_id": comment.get("id"),
                    "error": "issue does not expose exactly one machine-resolvable acceptance_actor",
                }
            )
            continue
        if record["actor"] != authorized_actor:
            defects.append(
                {
                    "comment_id": comment.get("id"),
                    "error": "acceptance actor does not match issue authorization",
                }
            )
            continue

        parsed.append(
            {
                "record": record,
                "comment_id": comment.get("id"),
                "issue_url": comment.get("issue_url"),
                "comment_url": comment.get("html_url") or comment.get("url"),
            }
        )

    matches = []
    for item in parsed:
        record = item["record"]
        state_producing = (
            record["record_type"] == "bootstrap-acceptance"
            or (
                record["record_type"] == "governance-acceptance"
                and record["stage"] == "build"
            )
        )
        if (
            state_producing
            and record["disposition"] == "accepted"
            and record.get("resulting_accepted_state") == accepted_sha
            and record["candidate_id"] == accepted_sha
        ):
            matches.append(item)

    if defects or not matches:
        if not matches:
            defects.append(
                "accepted ref has no matching accepted bootstrap/build acceptance record"
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
        if not isinstance(item, dict) or item.get("issue_url") not in issue_by_url:
            continue
        enriched = dict(item)
        enriched["issue_body"] = issue_by_url[item["issue_url"]].get("body")
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
            comments = github_issue_comments(repo)
            report = resolve_accepted_state(sha, comments)
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
