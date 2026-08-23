#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import urllib.request
from pathlib import Path


def run(args, *, cwd: Path, allowed=(0,)) -> subprocess.CompletedProcess:
    proc = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if proc.returncode not in allowed:
        detail = (proc.stderr or proc.stdout).strip()
        raise SystemExit(f"FS0 bootstrap prerequisite failed: {' '.join(args)}: {detail}")
    return proc


def require_command(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"FS0 bootstrap prerequisite failed: required command not found: {name}")
    return path


def parse_github_remote(url: str) -> str:
    patterns = (
        r"^https://github\.com/([^/]+/[^/]+?)(?:\.git)?$",
        r"^git@github\.com:([^/]+/[^/]+?)(?:\.git)?$",
        r"^ssh://git@github\.com/([^/]+/[^/]+?)(?:\.git)?$",
    )
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1)
    raise SystemExit("FS0 bootstrap prerequisite failed: origin is not a supported GitHub remote")


def probe_dns_tls() -> None:
    try:
        socket.getaddrinfo("api.github.com", 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise SystemExit(f"FS0 bootstrap prerequisite failed: GitHub DNS resolution failed: {exc}")

    context = ssl.create_default_context()
    request = urllib.request.Request(
        "https://api.github.com/meta",
        headers={"User-Agent": "fs0-bootstrap-preflight"},
    )
    try:
        with urllib.request.urlopen(request, context=context, timeout=15) as response:
            if response.status != 200:
                raise SystemExit(
                    f"FS0 bootstrap prerequisite failed: GitHub HTTPS probe returned {response.status}"
                )
    except Exception as exc:
        raise SystemExit(f"FS0 bootstrap prerequisite failed: GitHub HTTPS/TLS access failed: {exc}")


def gh_json(root: Path, *path: str):
    proc = run(["gh", "api", *path], cwd=root)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"FS0 bootstrap prerequisite failed: GitHub API returned invalid JSON: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="FS0 bootstrap operating-substrate preflight")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path.cwd().resolve()
    if not (root / ".git").is_dir():
        raise SystemExit("FS0 bootstrap prerequisite failed: target is not a user-initialized Git repository")

    for command in ("git", "gh", "python3"):
        require_command(command)

    origin = run(["git", "remote", "get-url", "origin"], cwd=root).stdout.strip()
    repository = parse_github_remote(origin)

    probe_dns_tls()

    run(["git", "rev-parse", "--git-dir"], cwd=root)
    run(["git", "ls-remote", "origin", "HEAD"], cwd=root)
    run(["gh", "auth", "status", "-h", "github.com"], cwd=root)

    actor = gh_json(root, "user").get("login")
    if not isinstance(actor, str) or not actor:
        raise SystemExit("FS0 bootstrap prerequisite failed: authenticated GitHub actor could not be resolved")

    repo = gh_json(root, f"repos/{repository}")
    permissions = repo.get("permissions") or {}
    if permissions.get("push") is not True:
        raise SystemExit("FS0 bootstrap prerequisite failed: authenticated actor lacks repository push capability")
    if repo.get("has_issues") is not True:
        raise SystemExit("FS0 bootstrap prerequisite failed: GitHub Issues are not enabled")

    # Non-mutating API reads for the GitHub object classes required by FS0.
    gh_json(root, f"repos/{repository}/issues?per_page=1")
    gh_json(root, f"repos/{repository}/pulls?per_page=1")
    gh_json(root, f"repos/{repository}/actions/runs?per_page=1")
    gh_json(root, f"repos/{repository}/commits/HEAD/status")
    gh_json(root, f"repos/{repository}/git/ref/heads/{run(['git','branch','--show-current'], cwd=root).stdout.strip()}")

    # Dry-run publication probes verify Git authentication and ref publication
    # capability without changing remote repository state.
    branch = run(["git", "branch", "--show-current"], cwd=root).stdout.strip()
    if not branch:
        raise SystemExit("FS0 bootstrap prerequisite failed: detached HEAD is not supported")
    run(["git", "push", "--dry-run", "origin", f"HEAD:refs/heads/{branch}"], cwd=root)
    run(["git", "push", "--dry-run", "origin", "HEAD:refs/heads/accepted"], cwd=root)

    workflow = root / ".github/workflows/fs0-conformance.yml"
    if not workflow.is_file():
        raise SystemExit("FS0 bootstrap prerequisite failed: canonical Conformance workflow is missing")
    workflow_text = workflow.read_text(encoding="utf-8")
    for marker in ("push:", "pull_request:", "workflow_dispatch:"):
        if marker not in workflow_text:
            raise SystemExit(
                f"FS0 bootstrap prerequisite failed: canonical Conformance workflow lacks {marker}"
            )

    result = {
        "schema_version": "1",
        "record_type": "fs0-operating-substrate-preflight",
        "repository": repository,
        "actor": actor,
        "git_remote": origin,
        "capabilities": {
            "git_repository_inspection": True,
            "git_remote_read": True,
            "git_authenticated_push_dry_run": True,
            "github_api_authentication": True,
            "dns_resolution": True,
            "https_tls": True,
            "issue_read": True,
            "pull_request_read": True,
            "workflow_read": True,
            "commit_status_read": True,
            "git_ref_read": True,
            "event_driven_conformance_workflow": True,
            "accepted_state_publication_dry_run": True,
            "authenticated_actor_resolution": True,
            "maintained_script_execution": True,
            "remote_conformance_evidence_retrieval": True,
        },
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"FS0 bootstrap operating-substrate preflight: PASS ({repository}, actor={actor})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
