#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _run(args, *, input_text=None, allowed=(0,)):
    proc = subprocess.run(args, text=True, input=input_text, capture_output=True)
    if proc.returncode not in allowed:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"{' '.join(args)} failed ({proc.returncode}): {detail}")
    return proc


def _git(*args, allowed=(0,)):
    return _run(["git", *args], allowed=allowed)


def _gh(endpoint, *, method="GET", payload=None):
    args = ["gh", "api", endpoint]
    input_text = None
    if method != "GET":
        args += ["--method", method]
    if payload is not None:
        args += ["--input", "-"]
        input_text = json.dumps(payload)
    proc = _run(args, input_text=input_text)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"gh api returned invalid JSON for {endpoint}: {exc}")


def _root():
    root = Path.cwd().resolve()
    if not (root / ".git").exists():
        raise RuntimeError("bootstrap-cutover must run from repository root")
    return root


def _load_module(path, name):
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = old


def _origin_repo():
    raw = _git("remote", "get-url", "origin").stdout.rstrip("\r\n")
    for prefix in ("https://github.com/", "git@github.com:"):
        if raw.startswith(prefix):
            value = raw[len(prefix):]
            if value.endswith(".git"):
                value = value[:-4]
            return value
    raise RuntimeError(f"unsupported origin URL: {raw}")


def _remote_main():
    proc = _git("ls-remote", "--heads", "origin", "refs/heads/main")
    fields = proc.stdout.split()
    if len(fields) != 2 or fields[1] != "refs/heads/main":
        raise RuntimeError("unable to resolve origin/main")
    return fields[0].lower()


def _status_paths():
    proc = _git("status", "--porcelain=v1", "--untracked-files=all")
    paths = []
    for raw in proc.stdout.splitlines():
        line = raw.rstrip("\r\n")
        if not line:
            continue
        if len(line) < 4 or line[2] != " ":
            raise RuntimeError(f"unexpected porcelain record: {line!r}")
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path)
    return sorted(paths)


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _validate(root):
    gen = _run([str(root / "repo/bootstrap/scripts/bootstrap"), "--check"])
    val = _run([str(root / "repo/scripts/validate"), "--json"])
    report = json.loads(val.stdout)
    if report.get("status") != "pass":
        raise RuntimeError("canonical Conformance did not report pass")
    return {
        "generation": gen.stdout.strip(),
        "passed_assertions": report.get("passed_assertions"),
        "failed_assertions": report.get("failed_assertions"),
    }


def _commit_and_push(root, message, expected_remote):
    _git("add", "-A")
    _run(["git", "diff", "--cached", "--check"])
    _git("commit", "-m", message)
    sha = _git("rev-parse", "HEAD").stdout.rstrip("\r\n").lower()
    if _remote_main() != expected_remote:
        raise RuntimeError("origin/main changed concurrently before push")
    _git("push", "origin", "main")
    if _remote_main() != sha:
        raise RuntimeError("origin/main verification failed after push")
    if _status_paths():
        raise RuntimeError("worktree is not clean after push")
    return sha


def main():
    parser = argparse.ArgumentParser(
        prog="repo/scripts/bootstrap-cutover",
        description="Perform the complete initial FS0 bootstrap acceptance and cutover.",
    )
    parser.add_argument(
        "--accept-bootstrap",
        action="store_true",
        help="explicitly accept the validated bootstrap candidate for initial cutover",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = {
        "schema_version": "1",
        "record_type": "bootstrap-cutover-result",
        "status": "error",
        "initial_revision": None,
        "candidate_revision": None,
        "cutover_revision": None,
        "bootstrap_provenance_issue": None,
        "acceptance_comment_id": None,
        "acceptance_receipt_ref": None,
        "acceptance_receipt_object_sha": None,
        "issue_closed": False,
        "validation": [],
        "errors": [],
    }

    try:
        if not args.accept_bootstrap:
            raise RuntimeError(
                "bootstrap acceptance is explicit; rerun with --accept-bootstrap after reviewing the candidate"
            )

        root = _root()
        if _status_paths():
            raise RuntimeError("working tree must be clean before bootstrap cutover")
        if _git("branch", "--show-current").stdout.rstrip("\r\n") != "main":
            raise RuntimeError("bootstrap cutover requires branch main")

        initial = _git("rev-parse", "HEAD").stdout.rstrip("\r\n").lower()
        result["initial_revision"] = initial
        if _remote_main() != initial:
            raise RuntimeError("local HEAD and origin/main must agree before cutover")

        state_source = root / "repo/bootstrap/data/state/bootstrap.json"
        state = _load(state_source)
        if (
            state.get("state") != "candidate"
            or state.get("candidate_revision") is not None
            or state.get("first_accepted_fs0_revision") is not None
            or state.get("bootstrap_provenance_issue") is not None
            or state.get("bootstrap_acceptance_record") is not None
            or state.get("cutover_timestamp") is not None
            or state.get("accepted_ref") != "refs/heads/main"
        ):
            raise RuntimeError("repository is not a fresh unaccepted bootstrap candidate")

        accepted_state = _load_module(
            root / "repo/governance/accepted_state.py",
            "fs0_bootstrap_cutover_accepted_state",
        )
        repo = _origin_repo()

        actor_data = _gh("user")
        actor = {"id": actor_data.get("id"), "login": actor_data.get("login")}
        if not isinstance(actor["id"], int) or actor["id"] < 1 or not actor["login"]:
            raise RuntimeError("unable to resolve authenticated GitHub actor")

        issue_body = (
            "# FS0 Bootstrap Provenance\n\n"
            "Dedicated provenance anchor for initial FS0 bootstrap verification, "
            "semantic audit, explicit acceptance, immutable receipt publication, and cutover.\n\n"
            "```json\n"
            + json.dumps({
                "schema_version": "1",
                "record_type": "bootstrap-provenance",
                "bootstrap_revision": initial,
                "bootstrap_authorization": {"acceptance_actor": actor},
            }, indent=2)
            + "\n```\n"
        )
        issue = _gh(
            f"repos/{repo}/issues",
            method="POST",
            payload={"title": "FS0 bootstrap provenance and acceptance", "body": issue_body},
        )
        issue_number = issue.get("number")
        if not isinstance(issue_number, int) or issue_number < 1:
            raise RuntimeError("GitHub did not return a bootstrap provenance issue number")
        result["bootstrap_provenance_issue"] = issue_number

        state["bootstrap_provenance_issue"] = issue_number
        _save(state_source, state)
        _run([str(root / "repo/bootstrap/scripts/bootstrap")])
        result["validation"].append({"stage": "candidate", **_validate(root)})
        candidate = _commit_and_push(
            root,
            "Bind FS0 bootstrap candidate to provenance",
            initial,
        )
        result["candidate_revision"] = candidate

        acceptance_record = {
            "schema_version": "1",
            "record_type": "bootstrap-acceptance",
            "acceptance_id": f"FS0-BOOTSTRAP-ACCEPT-{candidate[:12]}",
            "stage": "bootstrap",
            "work_id": "FS0-BOOTSTRAP",
            "candidate_id": candidate,
            "disposition": "accepted",
            "actor": actor,
            "evidence": [
                {
                    "type": "bootstrap-verification",
                    "candidate_id": candidate,
                    "result": "pass",
                    "entrypoint": "repo/scripts/validate",
                },
                {
                    "type": "bootstrap-semantic-audit",
                    "candidate_id": candidate,
                    "result": "satisfied",
                    "basis": "explicit --accept-bootstrap invocation after canonical validation",
                },
            ],
            "decision_timestamp": _now(),
            "resulting_accepted_state": candidate,
        }
        acceptance_body = (
            accepted_state.MARKER + "\n```json\n"
            + json.dumps(acceptance_record, indent=2)
            + "\n```"
        )
        comment = _gh(
            f"repos/{repo}/issues/{issue_number}/comments",
            method="POST",
            payload={"body": acceptance_body},
        )
        comment_id = comment.get("id")
        if not isinstance(comment_id, int) or comment_id < 1:
            raise RuntimeError("GitHub did not return an acceptance comment ID")
        result["acceptance_comment_id"] = comment_id

        pub = _run([
            str(root / "repo/scripts/publish-accepted"),
            "--candidate", candidate,
            "--json",
        ])
        publication = json.loads(pub.stdout)
        if publication.get("status") != "published":
            raise RuntimeError("accepted-state publication failed")
        result["acceptance_receipt_ref"] = publication.get("acceptance_receipt_ref")
        result["acceptance_receipt_object_sha"] = publication.get("acceptance_receipt_object_sha")

        matching = [
            item for item in publication.get("acceptance_records", [])
            if item.get("record", {}).get("record_type") == "bootstrap-acceptance"
            and item.get("record", {}).get("candidate_id") == candidate
            and item.get("record", {}).get("disposition") == "accepted"
        ]
        if len(matching) != 1:
            raise RuntimeError("publication did not expose exactly one bootstrap acceptance record")
        embedded_acceptance = matching[0]["record"]

        state = _load(state_source)
        state.update({
            "state": "cutover",
            "candidate_revision": None,
            "first_accepted_fs0_revision": candidate,
            "bootstrap_provenance_issue": issue_number,
            "bootstrap_acceptance_record": embedded_acceptance,
            "accepted_ref": "refs/heads/main",
            "cutover_timestamp": _now(),
        })
        _save(state_source, state)
        _run([str(root / "repo/bootstrap/scripts/bootstrap")])
        result["validation"].append({"stage": "cutover", **_validate(root)})
        cutover = _commit_and_push(
            root,
            "Complete FS0 bootstrap cutover",
            candidate,
        )
        result["cutover_revision"] = cutover

        resolved = _run([str(root / "repo/scripts/accepted-state"), "--json"])
        resolved_report = json.loads(resolved.stdout)
        if resolved_report.get("status") != "accepted":
            raise RuntimeError("post-cutover accepted-state resolution failed")

        branches = _git("ls-remote", "--heads", "origin").stdout.splitlines()
        names = sorted(line.split()[1] for line in branches if line.split())
        if names != ["refs/heads/main"]:
            raise RuntimeError(f"unexpected persistent remote branches: {names}")

        closed = _gh(
            f"repos/{repo}/issues/{issue_number}",
            method="PATCH",
            payload={"state": "closed"},
        )
        if closed.get("state") != "closed":
            raise RuntimeError("bootstrap provenance issue did not close")
        verify_issue = _gh(f"repos/{repo}/issues/{issue_number}")
        if verify_issue.get("state") != "closed":
            raise RuntimeError("bootstrap provenance issue closure verification failed")
        result["issue_closed"] = True

        result["status"] = "pass"
    except Exception as exc:
        result["errors"].append(str(exc))

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("FS0 bootstrap cutover: " + result["status"].upper())
        if result.get("candidate_revision"):
            print("Candidate: " + result["candidate_revision"])
        if result.get("cutover_revision"):
            print("Cutover: " + result["cutover_revision"])
        if result.get("bootstrap_provenance_issue"):
            print("Issue: #" + str(result["bootstrap_provenance_issue"]))
        print("Issue closed: " + str(result["issue_closed"]).lower())
        for error in result["errors"]:
            print("Error: " + error, file=sys.stderr)

    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
