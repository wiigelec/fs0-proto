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

def _run(args, cwd=None, allowed=(0,), input_text=None):
    proc = subprocess.run(args, cwd=cwd, text=True, input=input_text, capture_output=True)
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

def _gh_json(endpoint):
    proc = _run(["gh","api",endpoint])
    try:
        value = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SelfChangeError(f"GitHub API returned invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise SelfChangeError("GitHub API response must be an object")
    return value

def origin_repository(root):
    remote = _run(["git","remote","get-url","origin"], cwd=root).stdout.strip()
    for prefix in ("https://github.com/","git@github.com:"):
        if remote.startswith(prefix):
            value = remote[len(prefix):]
            return value[:-4] if value.endswith(".git") else value
    raise SelfChangeError("origin must resolve to github.com owner/repository")

def governed_work_from_issue(root, issue_number):
    issue = _gh_json(f"repos/{origin_repository(root)}/issues/{issue_number}")
    if "pull_request" in issue:
        raise SelfChangeError("governed work identity must resolve to a GitHub issue")
    matches = [obj for obj in _json_fence_objects(issue.get("body")) if obj.get("record_type") == "governed-work"]
    if len(matches) != 1:
        raise SelfChangeError("governed issue must expose exactly one governed-work record")
    work_module = load_module(root / "repo/governance/work.py", "fs0_self_change_binding_work")
    try:
        return work_module.validate_work(dict(matches[0]))
    except Exception as exc:
        raise SelfChangeError(f"governed issue work record is invalid: {exc}") from exc

REPO_PIN_PATH = Path("repo/state/repo-pin.json")


def utc_timestamp():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def repo_pin_blob_at(root, revision):
    proc = _run(
        ["git", "rev-parse", f"{revision}:repo/state/repo-pin.json"],
        cwd=root, allowed=(0, 128),
    )
    if proc.returncode != 0:
        return None
    value = proc.stdout.strip().lower()
    return value if SHA_RE.fullmatch(value) else None


def create_pinned_candidate(root, source_candidate, issue_number):
    source_candidate = exact_candidate(source_candidate)
    work = governed_work_from_issue(root, issue_number)
    predecessor = remote_ref("refs/heads/main")
    if predecessor is None:
        raise SelfChangeError("refs/heads/main must exist before governed candidate pinning")
    prior_sha = repo_pin_blob_at(root, predecessor)
    if prior_sha is None:
        raise SelfChangeError("governed candidate requires prior accepted repo pin")
    pin = {
        "source_commit": source_candidate,
        "prior_sha": prior_sha,
        "timestamp": utc_timestamp(),
    }
    content = json.dumps(pin, indent=2) + "\n"
    pin_sha = _run(["git", "hash-object", "-w", "--stdin"], cwd=root, input_text=content).stdout.strip().lower()

    index = root / ".git" / "fs0-repo-pin-index"
    env = dict(__import__("os").environ)
    env["GIT_INDEX_FILE"] = str(index)
    try:
        subprocess.run(["git", "read-tree", source_candidate], cwd=root, env=env, check=True)
        subprocess.run(
            ["git", "update-index", "--add", "--cacheinfo", "100644", pin_sha, str(REPO_PIN_PATH)],
            cwd=root, env=env, check=True,
        )
        tree = subprocess.run(
            ["git", "write-tree"], cwd=root, env=env, text=True,
            capture_output=True, check=True,
        ).stdout.strip()
    finally:
        try:
            index.unlink()
        except FileNotFoundError:
            pass

    binding = {
        "schema_version": "1", "record_type": "governed-candidate-binding",
        "issue_number": issue_number,
        "accepted_repository_predecessor": predecessor,
        "base_ref": "refs/heads/main",
        "repo_pin_sha": pin_sha,
        "governed_work": work,
    }
    message = (
        "Pin FS0 governed candidate\n\n"
        "```json\n" + json.dumps(binding, indent=2, sort_keys=True) + "\n```\n"
    )
    pinned = _run(
        ["git", "commit-tree", tree, "-p", source_candidate],
        cwd=root, input_text=message,
    ).stdout.strip().lower()
    return exact_candidate(pinned), pin_sha

def bind_candidate(root, candidate, issue_number):
    pinned, _ = create_pinned_candidate(root, candidate, issue_number)
    return pinned

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
        description="Create and publish a final repo-pin commit for a governed candidate.",
    )
    parser.add_argument("--candidate", required=True, help="exact last mutation commit SHA")
    parser.add_argument("--issue", required=True, type=int, help="governed GitHub issue number")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = repository_root()
    report = {
        "schema_version": "1", "record_type": "self-change-candidate-publication",
        "status": "error", "source_candidate_id": None, "candidate_id": None,
        "repo_pin_sha": None, "governed_issue_number": args.issue, "errors": [],
    }
    try:
        source = exact_candidate(args.candidate)
        report["source_candidate_id"] = source
        pinned, pin_sha = create_pinned_candidate(root, source, args.issue)
        report["repo_pin_sha"] = pin_sha
        report.update(publish_candidate(root, pinned))
    except Exception as exc:
        report["errors"].append(str(exc))
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("FS0 candidate publication: " + report["status"].upper())
        if report.get("candidate_id"):
            print("Pinned candidate: " + report["candidate_id"])
            print("Repo pin: " + report["repo_pin_sha"])
        for error in report["errors"]:
            print("Error: " + error, file=sys.stderr)
    return 0 if report["status"] == "published" else 1

if __name__ == "__main__":
    raise SystemExit(main())
