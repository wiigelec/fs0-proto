#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def _run(args, allowed=(0,)):
    proc = subprocess.run(args, text=True, capture_output=True)
    if proc.returncode not in allowed:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"{' '.join(args)} failed ({proc.returncode}): {detail}")
    return proc


def repository_root():
    root = Path.cwd().resolve()
    if not (root / ".git").exists():
        raise RuntimeError("repo/scripts/publish-accepted must be invoked from repository root")
    return root


def load_accepted_state(root):
    module_path = root / "repo/governance/accepted_state.py"
    if not module_path.is_file():
        raise RuntimeError("accepted-state resolver is missing")
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("fs0_accepted_state", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = old


def exact_commit(root, value):
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        raise RuntimeError("candidate must be an exact 40-hex Git commit SHA")
    candidate = value.lower()
    proc = _run(["git", "cat-file", "-e", f"{candidate}^{{commit}}"], allowed=(0, 1, 128))
    if proc.returncode != 0:
        raise RuntimeError("candidate does not resolve to a local Git commit")
    resolved = _run(["git", "rev-parse", f"{candidate}^{{commit}}"]).stdout.strip().lower()
    if resolved != candidate:
        raise RuntimeError("candidate must name the exact commit object")
    return candidate


def remote_accepted_ref():
    proc = _run(["git", "ls-remote", "--heads", "origin", "refs/heads/accepted"])
    text = proc.stdout.strip()
    if not text:
        return None
    fields = text.split()
    if len(fields) != 2 or fields[1] != "refs/heads/accepted":
        raise RuntimeError("unexpected accepted-ref resolution")
    return fields[0].lower()


def state_producing_record(record, candidate):
    return (
        record.get("disposition") == "accepted"
        and record.get("candidate_id") == candidate
        and record.get("resulting_accepted_state") == candidate
        and (
            record.get("record_type") == "bootstrap-acceptance"
            or (
                record.get("record_type") == "governance-acceptance"
                and record.get("stage") == "build"
            )
        )
    )


def publication_decision(candidate, current_accepted, comments, accepted_state_module):
    candidate_report = accepted_state_module.resolve_accepted_state(candidate, comments)
    if candidate_report.get("status") != "accepted":
        return {
            "allowed": False,
            "action": "deny",
            "reason": "candidate lacks a matching explicit accepted bootstrap/build acceptance record",
            "candidate_report": candidate_report,
        }

    matching = [
        item
        for item in candidate_report.get("acceptance_records", [])
        if state_producing_record(item.get("record", {}), candidate)
    ]
    if not matching:
        return {
            "allowed": False,
            "action": "deny",
            "reason": "candidate acceptance record is not state-producing",
            "candidate_report": candidate_report,
        }

    if current_accepted is None:
        return {
            "allowed": True,
            "action": "create",
            "reason": "explicit acceptance exists before accepted-ref creation",
            "candidate_report": candidate_report,
        }

    if current_accepted == candidate:
        return {
            "allowed": True,
            "action": "noop",
            "reason": "accepted ref already matches explicitly accepted candidate",
            "candidate_report": candidate_report,
        }

    current_report = accepted_state_module.resolve_accepted_state(current_accepted, comments)
    if current_report.get("status") != "accepted":
        return {
            "allowed": False,
            "action": "deny",
            "reason": "current accepted ref is not backed by a valid acceptance record",
            "candidate_report": candidate_report,
            "current_report": current_report,
        }

    return {
        "allowed": True,
        "action": "advance",
        "reason": "explicit candidate acceptance exists before accepted-ref advance",
        "candidate_report": candidate_report,
        "current_report": current_report,
    }


def ensure_fast_forward(current_accepted, candidate):
    if current_accepted is None or current_accepted == candidate:
        return
    proc = _run(
        ["git", "merge-base", "--is-ancestor", current_accepted, candidate],
        allowed=(0, 1, 128),
    )
    if proc.returncode != 0:
        raise RuntimeError("accepted ref may advance only by fast-forward")


def main():
    parser = argparse.ArgumentParser(
        prog="repo/scripts/publish-accepted",
        description="Publish an explicitly accepted FS0 repository revision.",
    )
    parser.add_argument("--candidate", required=True, help="exact accepted commit SHA")
    parser.add_argument("--json", action="store_true", help="emit structured JSON")
    args = parser.parse_args()

    report = {
        "schema_version": "1",
        "record_type": "accepted-state-publication-result",
        "status": "error",
        "candidate_id": None,
        "previous_accepted_revision": None,
        "published_revision": None,
        "action": None,
        "acceptance_records": [],
        "errors": [],
    }

    try:
        root = repository_root()
        if _run(["git", "status", "--porcelain", "--untracked-files=all"]).stdout.strip():
            raise RuntimeError("working tree must be clean before accepted-state publication")

        module = load_accepted_state(root)
        candidate = exact_commit(root, args.candidate)
        report["candidate_id"] = candidate

        repo = module.origin_repository(root)
        comments = module.github_issue_comments(repo)
        current = remote_accepted_ref()
        report["previous_accepted_revision"] = current

        decision = publication_decision(candidate, current, comments, module)
        report["action"] = decision["action"]
        report["acceptance_records"] = decision.get("candidate_report", {}).get(
            "acceptance_records", []
        )
        if not decision["allowed"]:
            raise RuntimeError(decision["reason"])

        ensure_fast_forward(current, candidate)

        # Re-read the remote ref immediately before mutation. A concurrent change
        # aborts publication rather than being silently incorporated.
        observed = remote_accepted_ref()
        if observed != current:
            raise RuntimeError("accepted ref changed concurrently; refusing publication")

        if decision["action"] in {"create", "advance"}:
            proc = _run(
                ["git", "push", "origin", f"{candidate}:refs/heads/accepted"],
                allowed=(0,),
            )
            report["push_output"] = (proc.stdout + proc.stderr).strip()
        elif decision["action"] != "noop":
            raise RuntimeError(f"unexpected publication action: {decision['action']}")

        final = remote_accepted_ref()
        if final != candidate:
            raise RuntimeError("accepted ref does not match candidate after publication")

        # Canonical accepted state must resolve from ref + matching record after push.
        comments_after = module.github_issue_comments(repo)
        resolved = module.resolve_accepted_state(final, comments_after)
        if resolved.get("status") != "accepted":
            raise RuntimeError("published accepted ref does not resolve to canonical accepted state")

        report["status"] = "published"
        report["published_revision"] = final
        report["resolved_state"] = resolved
    except Exception as exc:
        report["errors"].append(str(exc))

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"FS0 accepted-state publication: {report['status'].upper()}")
        if report.get("published_revision"):
            print(f"Revision: {report['published_revision']}")
        for error in report["errors"]:
            print(f"Error: {error}", file=sys.stderr)

    return 0 if report["status"] == "published" else 1


if __name__ == "__main__":
    raise SystemExit(main())
