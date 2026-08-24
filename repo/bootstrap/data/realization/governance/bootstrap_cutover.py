#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

BRANCH = "fs0-bootstrap-cutover"

def run(args, *, input_text=None, allowed=(0,)):
    p = subprocess.run(args, text=True, input=input_text, capture_output=True)
    if p.returncode not in allowed:
        raise RuntimeError(f"{' '.join(args)} failed ({p.returncode}): {p.stderr.strip() or p.stdout.strip()}")
    return p

def git(*args, allowed=(0,)):
    return run(["git", *args], allowed=allowed)

def gh(endpoint, *, method="GET", payload=None):
    args = ["gh", "api", endpoint]
    inp = None
    if method != "GET":
        args += ["--method", method]
    if payload is not None:
        args += ["--input", "-"]
        inp = json.dumps(payload)
    return json.loads(run(args, input_text=inp).stdout)

def root():
    r = Path.cwd().resolve()
    if not (r / ".git").exists():
        raise RuntimeError("run from repository root")
    return r

def repo_name():
    raw = git("remote", "get-url", "origin").stdout.strip()
    for prefix in ("https://github.com/", "git@github.com:"):
        if raw.startswith(prefix):
            s = raw[len(prefix):]
            return s[:-4] if s.endswith(".git") else s
    raise RuntimeError(f"unsupported origin URL: {raw}")

def remote_main():
    f = git("ls-remote", "--heads", "origin", "refs/heads/main").stdout.split()
    if len(f) != 2:
        raise RuntimeError("cannot resolve origin/main")
    return f[0].lower()

def status_paths():
    out = []
    for raw in git("status", "--porcelain=v1", "--untracked-files=all").stdout.splitlines():
        line = raw.rstrip("\r\n")
        if not line:
            continue
        if len(line) < 4:
            raise RuntimeError(f"unexpected porcelain: {line!r}")
        p = line[3:]
        if " -> " in p:
            p = p.split(" -> ", 1)[1]
        out.append(p)
    return sorted(out)

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def save(p, v):
    p.write_text(json.dumps(v, indent=2) + "\n", encoding="utf-8")

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")

def main():
    ap = argparse.ArgumentParser(description="Create the one-time FS0 bootstrap cutover PR.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = {
        "schema_version":"1",
        "record_type":"bootstrap-cutover-result",
        "status":"error",
        "base_revision":None,
        "candidate_revision":None,
        "bootstrap_provenance_issue":None,
        "branch":BRANCH,
        "pull_request":None,
        "errors":[]
    }
    try:
        r = root()
        if status_paths():
            raise RuntimeError("working tree must be clean")
        if git("branch","--show-current").stdout.strip() != "main":
            raise RuntimeError("must start on main")
        base = git("rev-parse","HEAD").stdout.strip().lower()
        result["base_revision"] = base
        if remote_main() != base:
            raise RuntimeError("local main and origin/main must match")
        state_path = r / "repo/bootstrap/data/state/bootstrap.json"
        state = load(state_path)
        if state.get("state") != "candidate":
            raise RuntimeError("bootstrap state is not candidate")
        repo = repo_name()
        actor = gh("user")
        issue = gh(f"repos/{repo}/issues", method="POST", payload={
            "title":"FS0 bootstrap provenance",
            "body":"# FS0 Bootstrap Provenance\n\nThis issue authorizes the one-time bootstrap cutover PR. "
                   "Merging the designated validated PR is the external semantic audit and explicit bootstrap acceptance.\n\n"
                   f"Base revision: `{base}`\nActor: `{actor.get('login')}` (`{actor.get('id')}`)\n"
        })
        ino = issue.get("number")
        if not isinstance(ino, int) or ino < 1:
            raise RuntimeError("failed to create provenance issue")
        result["bootstrap_provenance_issue"] = ino
        if git("ls-remote","--heads","origin",f"refs/heads/{BRANCH}").stdout.strip():
            raise RuntimeError(f"remote branch already exists: {BRANCH}")
        git("switch","-c",BRANCH)
        state.update({
            "state":"cutover",
            "candidate_revision":None,
            "first_accepted_fs0_revision":None,
            "bootstrap_provenance_issue":ino,
            "bootstrap_acceptance_record":{
                "schema_version":"1",
                "record_type":"pr-merge-acceptance",
                "issue_number":ino,
                "head_ref":f"refs/heads/{BRANCH}",
                "base_ref":"refs/heads/main"
            },
            "accepted_ref":"refs/heads/main",
            "cutover_timestamp":now()
        })
        save(state_path,state)
        run([str(r/"repo/bootstrap/scripts/bootstrap")])
        run([str(r/"repo/bootstrap/scripts/bootstrap"),"--check"])
        report = json.loads(run([str(r/"repo/scripts/validate"),"--json"]).stdout)
        if report.get("status") != "pass":
            raise RuntimeError("canonical validation failed")
        git("add","-A")
        run(["git","diff","--cached","--check"])
        git("commit","-m","Prepare FS0 bootstrap cutover")
        candidate = git("rev-parse","HEAD").stdout.strip().lower()
        result["candidate_revision"] = candidate
        git("push","-u","origin",BRANCH)
        pr = gh(f"repos/{repo}/pulls", method="POST", payload={
            "title":"FS0 bootstrap cutover",
            "head":BRANCH,
            "base":"main",
            "body":f"Governed by bootstrap provenance issue #{ino}.\n\nValidated candidate: `{candidate}`\n\n"
                   "Merging this PR is the external semantic audit and explicit bootstrap acceptance."
        })
        if pr.get("head",{}).get("sha") != candidate:
            raise RuntimeError("PR head does not match candidate")
        result["pull_request"] = {"number":pr.get("number"),"url":pr.get("html_url"),"head_sha":candidate}
        result["status"] = "awaiting-merge"
    except Exception as exc:
        result["errors"].append(str(exc))
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("FS0 bootstrap cutover: " + result["status"].upper())
        if result.get("pull_request"):
            print("PR: " + str(result["pull_request"]["url"]))
        for e in result["errors"]:
            print("Error: " + e, file=sys.stderr)
    return 0 if result["status"] == "awaiting-merge" else 1

if __name__ == "__main__":
    raise SystemExit(main())
