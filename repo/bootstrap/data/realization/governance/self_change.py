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
    proc = subprocess.run(
        args, cwd=cwd, text=True, capture_output=True
    )
    if proc.returncode not in allowed:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise SelfChangeError(
            f"{' '.join(args)} failed ({proc.returncode}): {detail}"
        )
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
    path = root / "repo/bootstrap/data/self_change_contract.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "record_type",
        "sequence",
        "candidate_ref",
        "accepted_ref",
        "entrypoint",
        "implementation",
        "dependencies",
    }
    if not isinstance(record, dict) or set(record) != required:
        raise SelfChangeError("self-change contract fields mismatch")
    if record["schema_version"] != "1":
        raise SelfChangeError("unsupported self-change contract schema")
    if record["record_type"] != "fs0-self-change-contract":
        raise SelfChangeError("unexpected self-change contract record_type")
    expected = [
        "accepted-authority",
        "candidate-publication",
        "conformance",
        "assurance",
        "explicit-acceptance",
        "accepted-state-publication",
    ]
    if record["sequence"] != expected:
        raise SelfChangeError("self-change sequence mismatch")
    return record


def exact_candidate(value):
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        raise SelfChangeError("candidate must be an exact 40-hex SHA")
    return value.lower()


def candidate_publication_decision(candidate, current_candidate):
    candidate = exact_candidate(candidate)
    if current_candidate is None:
        return {
            "allowed": True,
            "action": "create",
            "candidate_id": candidate,
        }
    current = exact_candidate(current_candidate)
    if current == candidate:
        return {
            "allowed": True,
            "action": "noop",
            "candidate_id": candidate,
        }
    return {
        "allowed": True,
        "action": "advance",
        "candidate_id": candidate,
        "previous_candidate": current,
    }


def remote_ref(ref):
    proc = _run(
        ["git", "ls-remote", "--heads", "origin", ref]
    )
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
    resolved = _run(
        ["git", "rev-parse", f"{candidate}^{{commit}}"],
        cwd=root,
    ).stdout.strip().lower()
    if resolved != candidate:
        raise SelfChangeError("candidate does not resolve exactly")

    ref = contract["candidate_ref"]
    current = remote_ref(ref)
    decision = candidate_publication_decision(candidate, current)

    if current and current != candidate:
        ff = _run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                current,
                candidate,
            ],
            cwd=root,
            allowed=(0, 1, 128),
        )
        if ff.returncode != 0:
            raise SelfChangeError(
                "candidate ref may advance only by fast-forward"
            )

    observed = remote_ref(ref)
    if observed != current:
        raise SelfChangeError(
            "candidate ref changed concurrently; refusing publication"
        )

    if decision["action"] in {"create", "advance"}:
        _run(
            ["git", "push", "origin", f"{candidate}:{ref}"],
            cwd=root,
        )
    final = remote_ref(ref)
    if final != candidate:
        raise SelfChangeError(
            "candidate ref does not match published candidate"
        )
    return {
        "schema_version": "1",
        "record_type": "candidate-publication-result",
        "status": "published",
        "candidate_id": candidate,
        "candidate_ref": ref,
        "action": decision["action"],
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
    acceptance_comment,
    accepted_publication,
):
    contract = load_contract(root)
    work = load_module(
        root / contract["dependencies"]["work"],
        "fs0_self_change_work",
    )
    accepted_state = load_module(
        root / contract["dependencies"]["accepted_state"],
        "fs0_self_change_accepted_state",
    )
    accepted_pub = load_module(
        root / contract["dependencies"]["accepted_publication"],
        "fs0_self_change_publish_accepted",
    )

    plan = work.validate_work(dict(accepted_plan))
    if plan["stage"] != "plan" or plan["disposition"] != "accepted":
        raise SelfChangeError(
            "self-change requires accepted Plan authority"
        )

    build = work.validate_work(dict(pending_build))
    if (
        build["stage"] != "build"
        or build["disposition"] != "pending"
        or build["accepted_plan_id"] != plan["work_id"]
        or build["predecessor_id"] != plan["work_id"]
    ):
        raise SelfChangeError(
            "pending Build does not derive from accepted Plan"
        )
    if not set(build["scope"]) <= set(
        plan["realization_intent"]["build_scope"]
    ):
        raise SelfChangeError(
            "Build scope exceeds accepted Plan build_scope"
        )

    candidate = exact_candidate(
        candidate_publication.get("candidate_id")
    )
    if (
        candidate_publication.get("status") != "published"
        or candidate_publication.get("candidate_ref")
        != contract["candidate_ref"]
    ):
        raise SelfChangeError(
            "exact candidate is not published"
        )

    if (
        conformance_report.get("status") != "pass"
        or conformance_report.get("candidate_id") != candidate
        or conformance_report.get("failed_assertions")
    ):
        raise SelfChangeError(
            "candidate Conformance is not passing"
        )
    build = work.record_conformance(build, "pass")

    gate = work.assurance_gate(
        list(triggered_obligation_ids),
        list(assurance_cases),
        list(assurance_findings),
    )
    if not gate["eligible"]:
        raise SelfChangeError(
            "candidate Assurance is not satisfied"
        )

    accepted_build = work.decide(
        build,
        "accepted",
        list(triggered_obligation_ids),
        list(assurance_cases),
        list(assurance_findings),
    )

    record = accepted_state.parse_acceptance_comment(
        acceptance_comment
    )
    if (
        record.get("record_type") != "governance-acceptance"
        or record.get("stage") != "build"
        or record.get("work_id") != accepted_build["work_id"]
        or record.get("candidate_id") != candidate
        or record.get("disposition") != "accepted"
        or record.get("resulting_accepted_state") != candidate
        or record.get("actor")
        != accepted_build["bounded_authorization"][
            "acceptance_actor"
        ]
    ):
        raise SelfChangeError(
            "explicit Build acceptance does not match completed Build"
        )

    synthetic_issue_body = (
        "```json\n"
        + json.dumps(accepted_build)
        + "\n```"
    )
    comments = [{
        "id": 1,
        "body": acceptance_comment,
        "issue_body": synthetic_issue_body,
    }]
    decision = accepted_pub.publication_decision(
        candidate,
        accepted_publication.get(
            "previous_accepted_revision"
        ),
        comments,
        accepted_state,
    )
    if not decision["allowed"]:
        raise SelfChangeError(
            "accepted-state publication is not authorized"
        )

    if (
        accepted_publication.get("status") != "published"
        or accepted_publication.get("published_revision")
        != candidate
        or accepted_publication.get("accepted_ref")
        != contract["accepted_ref"]
    ):
        raise SelfChangeError(
            "accepted-state publication result mismatch"
        )

    return {
        "schema_version": "1",
        "record_type": "self-change-cycle-result",
        "status": "complete",
        "candidate_id": candidate,
        "build_work_id": accepted_build["work_id"],
        "sequence": list(contract["sequence"]),
        "candidate_ref": contract["candidate_ref"],
        "accepted_ref": contract["accepted_ref"],
    }


def repository_root():
    root = Path.cwd().resolve()
    if not (root / ".git").exists():
        raise SelfChangeError(
            "repo/scripts/self-change must run from repository root"
        )
    return root


def main():
    parser = argparse.ArgumentParser(
        prog="repo/scripts/self-change",
        description=(
            "Publish an exact FS0 candidate revision. "
            "Acceptance and accepted-state publication remain "
            "separate explicitly authorized steps."
        ),
    )
    parser.add_argument(
        "--candidate",
        required=True,
        help="exact candidate commit SHA",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit structured result",
    )
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
        publication = publish_candidate(
            root,
            args.candidate,
        )
        report.update(publication)
    except Exception as exc:
        report["errors"].append(str(exc))

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            "FS0 candidate publication: "
            + report["status"].upper()
        )
        for error in report["errors"]:
            print("Error: " + error, file=sys.stderr)
    return 0 if report["status"] == "published" else 1


if __name__ == "__main__":
    raise SystemExit(main())
