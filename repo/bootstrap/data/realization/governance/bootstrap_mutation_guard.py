#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit("FS0 post-cutover mutation guard: " + message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing required record: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON {path}: {exc}")


def load_work_module(root: Path):
    path = root / "repo/governance/work.py"
    if not path.is_file():
        fail("Governance work realization is missing")
    spec = importlib.util.spec_from_file_location("fs0_governance_work", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dirty_bootstrap_paths(root: Path):
    proc = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        fail("unable to inspect repository mutation state")
    paths = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        rel = line[3:]
        if rel.startswith("repo/bootstrap/"):
            paths.append(rel)
    return sorted(set(paths))


def authorize(root: Path):
    state = load_json(root / "repo/state/bootstrap.json")
    if (
        state.get("schema_version") != "1"
        or state.get("record_type") != "bootstrap-state"
    ):
        fail("installed bootstrap state has invalid envelope")

    lifecycle = state.get("state")
    if lifecycle == "candidate":
        return {
            "schema_version": "1",
            "record_type": "bootstrap-mutation-authorization",
            "state": "candidate",
            "authorized": True,
            "governance_work_id": None,
            "changed_bootstrap_paths": dirty_bootstrap_paths(root),
        }
    if lifecycle != "cutover":
        fail("installed bootstrap state is neither candidate nor cutover")

    changed = dirty_bootstrap_paths(root)
    if not changed:
        return {
            "schema_version": "1",
            "record_type": "bootstrap-mutation-authorization",
            "state": "cutover",
            "authorized": True,
            "governance_work_id": None,
            "changed_bootstrap_paths": [],
        }

    work_path_raw = os.environ.get("FS0_GOVERNED_BUILD_FILE")
    if not work_path_raw:
        fail(
            "cutover bootstrap mutation requires FS0_GOVERNED_BUILD_FILE "
            "naming an authorized Governance Build record"
        )
    work_path = Path(work_path_raw)
    if not work_path.is_absolute():
        work_path = root / work_path
    record = load_json(work_path)

    module = load_work_module(root)
    try:
        work = module.validate_work(record)
    except Exception as exc:
        fail(f"Governance Build record is invalid: {exc}")

    if work.get("stage") != "build":
        fail("post-cutover mutation requires Governance Build work")
    if work.get("disposition") != "pending":
        fail("post-cutover mutation is authorized only while Build is pending")
    if not work.get("accepted_plan_id"):
        fail("Governance Build does not resolve an accepted Plan")

    scope = work.get("bounded_authorization", {}).get("mutation_scope", [])
    missing = [path for path in changed if path not in scope]
    if missing:
        fail(
            "Governance Build mutation_scope does not authorize bootstrap paths: "
            + ", ".join(missing)
        )

    return {
        "schema_version": "1",
        "record_type": "bootstrap-mutation-authorization",
        "state": "cutover",
        "authorized": True,
        "governance_work_id": work.get("work_id"),
        "accepted_plan_id": work.get("accepted_plan_id"),
        "changed_bootstrap_paths": changed,
    }


def main() -> int:
    root = Path.cwd().resolve()
    if not (root / ".git").exists():
        fail("must be invoked from repository root")
    report = authorize(root)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
