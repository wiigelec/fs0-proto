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

class SelfChangeError(ValueError):
    pass

def _run(args, cwd=None, allowed=(0,)):
    proc = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if proc.returncode not in allowed:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise SelfChangeError(f"{' '.join(args)} failed ({proc.returncode}): {detail}")
    return proc

def load_module(path: Path, name: str):
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = old

def load_contract(root: Path):
    record = json.loads((root / "repo/bootstrap/data/self_change_contract.json").read_text(encoding="utf-8"))
    expected = [
        "accepted-authority",
        "candidate-publication",
        "conformance",
        "assurance",
        "authorized-pr-merge",
    ]
    if record.get("sequence") != expected:
        raise SelfChangeError("self-change sequence mismatch")
    return record

def exact_candidate(value):
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        raise SelfChangeError("candidate must be an exact 40-hex SHA")
    return value.lower()

def remote_ref(ref):
    proc = _run(["git", "ls-remote", "--heads", "origin", ref])
    text = proc.stdout.strip()
    if not text:
        return None
    fields = text.split()
    if len(fields) != 2 or fields[1] != ref:
        raise SelfChangeError(f"unexpected ref resolution: {ref}")
    return fields[0].lower()

def publish_candidate(root: Path, candidate: str, contract=None):
    contract = contract or load_contract(root)
    candidate = exact_candidate(candidate)
    resolved = _run(["git", "rev-parse", f"{candidate}^{{commit}}"], cwd=root).stdout.strip().lower()
    if resolved != candidate:
        raise SelfChangeError("candidate does not resolve exactly")
    ref = contract["candidate_ref"]
    current = remote_ref(ref)
    if current and current != candidate:
        ff = _run(["git", "merge-base", "--is-ancestor", current, candidate], cwd=root, allowed=(0, 1, 128))
        if ff.returncode != 0:
            raise SelfChangeError("candidate ref may advance only by fast-forward")
    if remote_ref(ref) != current:
        raise SelfChangeError("candidate ref changed concurrently; refusing publication")
    if current != candidate:
        _run(["git", "push", "origin", f"{candidate}:{ref}"], cwd=root)
    if remote_ref(ref) != candidate:
        raise SelfChangeError("candidate ref does not match published candidate")
    return {
        "schema_version": "1",
        "record_type": "candidate-publication-result",
        "status": "published",
        "candidate_id": candidate,
        "candidate_ref": ref,
    }

def verify_cycle(
    root: Path,
    accepted_plan,
    pending_build,
    candidate_publication,
    conformance_report,
    triggered_obligation_ids,
    assurance_cases,
    assurance_findings,
    pr_candidate,
    merge_event,
):
    contract = load_contract(root)
    work = load_module(root / contract["dependencies"]["work"], "fs0_self_change_work")
    plan = work.validate_work(dict(accepted_plan))
    if plan["stage"] != "plan" or plan["disposition"] != "accepted":
        raise SelfChangeError("self-change requires accepted Plan authority")
    build = work.validate_work(dict(pending_build))
    if (
        build["stage"] != "build"
        or build["disposition"] != "pending"
        or build["accepted_plan_id"] != plan["work_id"]
        or build["predecessor_id"] != plan["work_id"]
    ):
        raise SelfChangeError("pending Build does not derive from accepted Plan")
    candidate = exact_candidate(candidate_publication.get("candidate_id"))
    if (
        candidate_publication.get("status") != "published"
        or candidate_publication.get("candidate_ref") != contract["candidate_ref"]
    ):
        raise SelfChangeError("exact candidate is not published")
    if (
        conformance_report.get("status") != "pass"
        or conformance_report.get("candidate_id") != candidate
        or conformance_report.get("failed_assertions")
    ):
        raise SelfChangeError("candidate Conformance is not passing")
    build = work.record_conformance(build, "pass")
    gate = work.assurance_gate(
        list(triggered_obligation_ids),
        list(assurance_cases),
        list(assurance_findings),
    )
    if not gate["eligible"]:
        raise SelfChangeError("candidate Assurance is not satisfied")
    pr = work.validate_pr_candidate(build, dict(pr_candidate))
    if pr["head_sha"] != candidate:
        raise SelfChangeError("PR head does not match published candidate")
    accepted = work.merge_acceptance(
        build,
        pr,
        dict(merge_event),
        list(triggered_obligation_ids),
        list(assurance_cases),
        list(assurance_findings),
    )
    return {
        "schema_version": "1",
        "record_type": "self-change-cycle-result",
        "status": "complete",
        "candidate_id": candidate,
        "build_work_id": build["work_id"],
        "resulting_accepted_revision": accepted["resulting_accepted_revision"],
        "sequence": list(contract["sequence"]),
        "candidate_ref": contract["candidate_ref"],
        "accepted_ref": contract["accepted_ref"],
    }

def repository_root():
    root = Path.cwd().resolve()
    if not (root / ".git").exists():
        raise SelfChangeError("repo/scripts/self-change must run from repository root")
    return root

def main():
    parser = argparse.ArgumentParser(
        prog="repo/scripts/self-change",
        description="Publish an exact governed candidate for PR review and merge acceptance.",
    )
    parser.add_argument("--candidate", required=True, help="exact candidate commit SHA")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = repository_root()
    report = {
        "schema_version": "1",
        "record_type": "self-change-candidate-publication",
        "status": "error",
        "candidate_id": None,
        "errors": [],
    }
    try:
        report.update(publish_candidate(root, args.candidate))
    except Exception as exc:
        report["errors"].append(str(exc))
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("FS0 candidate publication: " + report["status"].upper())
        for error in report["errors"]:
            print("Error: " + error, file=sys.stderr)
    return 0 if report["status"] == "published" else 1

if __name__ == "__main__":
    raise SystemExit(main())
