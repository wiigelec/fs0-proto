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
    proc = _run(["git", "ls-remote", "--heads", "origin", "refs/heads/main"])
    text = proc.stdout.strip()
    if not text:
        return None
    fields = text.split()
    if len(fields) != 2 or fields[1] != "refs/heads/main":
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
    if len(matching) != 1:
        return {
            "allowed": False,
            "action": "deny",
            "reason": "candidate must have exactly one state-producing acceptance record",
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

    return {
        "allowed": True,
        "action": "advance",
        "reason": (
            "explicit candidate acceptance exists; caller must verify the current "
            "accepted revision through its immutable receipt"
        ),
        "candidate_report": candidate_report,
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


def receipt_source(decision):
    records = decision.get("candidate_report", {}).get("acceptance_records", [])
    if len(records) != 1:
        raise RuntimeError("publication decision does not expose exactly one receipt source")
    return records[0]


def ensure_acceptance_receipt(candidate, acceptance_item, module, report):
    payload = module.acceptance_receipt_payload(candidate, acceptance_item)
    tag_text = module.acceptance_receipt_tag_text(candidate, payload)
    expected_sha = module.acceptance_receipt_object_sha(candidate, payload)
    receipt_ref = module.acceptance_receipt_ref(candidate)

    report["acceptance_receipt_ref"] = receipt_ref
    report["acceptance_receipt_object_sha"] = expected_sha

    observed = module.remote_acceptance_receipt_sha(candidate)
    if observed is not None:
        if observed != expected_sha:
            raise RuntimeError("conflicting immutable acceptance receipt already exists")
        report["acceptance_receipt_action"] = "reuse"
        return expected_sha

    proc = subprocess.run(
        ["git", "mktag"],
        text=True,
        input=tag_text,
        capture_output=True,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"git mktag failed ({proc.returncode}): {detail}")
    actual_sha = proc.stdout.strip().lower()
    if actual_sha != expected_sha:
        raise RuntimeError("git mktag produced unexpected acceptance receipt object")

    pushed = _run(
        ["git", "push", "origin", f"{actual_sha}:{receipt_ref}"],
        allowed=(0,),
    )
    report["acceptance_receipt_push_output"] = (
        pushed.stdout + pushed.stderr
    ).strip()
    report["acceptance_receipt_action"] = "create"

    verified = module.remote_acceptance_receipt_sha(candidate)
    if verified != expected_sha:
        raise RuntimeError("remote acceptance receipt verification failed")
    return expected_sha



def main():
    parser = argparse.ArgumentParser(
        prog="repo/scripts/publish-accepted",
        description="Retired compatibility entrypoint; governed PR merge publishes accepted state.",
    )
    parser.add_argument("--candidate")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = {
        "schema_version": "1",
        "record_type": "accepted-state-publication-result",
        "status": "retired",
        "errors": [
            "publish-accepted is retired; merge an eligible governed pull request into refs/heads/main"
        ],
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("FS0 accepted-state publication: RETIRED")
        print(report["errors"][0], file=sys.stderr)
    return 2



if __name__ == "__main__":
    raise SystemExit(main())
