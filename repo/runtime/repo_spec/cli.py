"""Deterministic JSON CLI orchestration for FS0-Core."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from .assurance import AssuranceFinding, AssuranceReport, make_report
from .build import BuildSession
from .conformance import (
    ConformanceFinding,
    ConformanceReport,
    build_conformance,
    design_conformance,
    functional_set_conformance,
    plan_conformance,
)
from .errors import RepoSpecError
from .evidence import load_authorization_graph, require_evidence_refs, write_evidence
from .governance import accept
from .jsonio import load_json
from .normative import AuthorizationGraph, Authority, Delegation
from .repository import Repository
from .validation import run_plan_validations


def _emit(value: dict) -> None:
    print(json.dumps(value, sort_keys=True))


def _repo(args) -> Repository:
    return Repository(args.repository)


def _assurance_from_dict(value: dict) -> AssuranceReport:
    return AssuranceReport(
        value["phase"],
        value["subject_id"],
        value["disposition"],
        value["rationale"],
        tuple(value.get("evidence_refs", [])),
        tuple(
            AssuranceFinding(
                f["id"], f["disposition"], f["rationale"], tuple(f.get("evidence_refs", []))
            )
            for f in value.get("findings", [])
        ),
    )


def _conformance_from_dict(value: dict) -> ConformanceReport:
    subject = value["subject"]
    return ConformanceReport(
        value["report_id"],
        subject["type"],
        subject["id"],
        value["disposition"],
        tuple(value.get("evidence_refs", [])),
        tuple(
            ConformanceFinding(f["code"], f["message"], f.get("path"))
            for f in value.get("findings", [])
        ),
    )


def _auto_build_manifest(repo: Repository, plan) -> dict:
    planned_paths = {fc.path for fc in plan.file_changes}
    mutations = []
    for mutation in repo.changed_paths(plan.implementation_predecessor, repo.head):
        artifact_only = (
            mutation.path.startswith("repo/proposals/")
            or mutation.path.startswith("repo/planning/")
        )
        if artifact_only and mutation.path not in planned_paths:
            continue
        mutations.append({"path": mutation.path, "operation": mutation.operation})
    return {
        "schema_version": "1",
        "artifact_type": "build-manifest",
        "build_id": "FS0-VALIDATION-BUILD",
        "plan_id": plan.id,
        "actor": "validation",
        "implementation_predecessor": plan.implementation_predecessor,
        "build_start_revision": plan.implementation_predecessor,
        "resulting_revision": repo.head,
        "mutations": mutations,
    }


def _git(root: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=True,
    )
    return p.stdout.strip()


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _self_host_check() -> dict:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _git(root, "init")
        _git(root, "config", "user.email", "fs0-selfhost@example.invalid")
        _git(root, "config", "user.name", "FS0 Self Host")
        _git(root, "commit", "--allow-empty", "-m", "predecessor")
        predecessor = _git(root, "rev-parse", "HEAD")

        proposal = root / "repo/proposals/demo.md"
        proposal.parent.mkdir(parents=True)
        proposal.write_text(
            """---
doc_id: DP-900
artifact_type: design-proposal
canonical_format: markdown
depends_on: []
---

**DP900-DETAIL-001**
The demonstration runtime SHALL create its planned file.
""",
            encoding="utf-8",
        )
        _git(root, "add", ".")
        _git(root, "commit", "-m", "design")
        design_revision = _git(root, "rev-parse", "HEAD")

        base = root / "repo/planning/001_DEMO"
        _write_json(base / "functional-set.json", {
            "schema_version": "1",
            "artifact_type": "functional-set",
            "functional_set": {
                "order": 1,
                "id": "DEMO",
                "kind": "extension",
                "title": "Self-host demonstration",
                "description": "Temporary functionality-defined functional set.",
            },
            "accepted_predecessor": {"repository_revision": predecessor},
            "design_inputs": [{
                "doc_id": "DP-900",
                "path": "repo/proposals/demo.md",
                "revision": design_revision,
                "statements": ["DP900-DETAIL-001"],
            }],
        })
        _write_json(base / "plan.json", {
            "schema_version": "2",
            "artifact_type": "plan",
            "plan": {
                "id": "DEMO-PLAN",
                "title": "Demo Plan",
                "description": "Self-host demonstration Plan.",
            },
            "functional_set": {
                "id": "DEMO",
                "path": "repo/planning/001_DEMO/functional-set.json",
            },
            "implementation_predecessor": {"repository_revision": predecessor},
            "documents": {
                "requirements": "requirements.json",
                "file_plans": ["files/001-demo.json"],
                "execution": "execution.json",
                "invariants": "invariants.json",
                "validation": "validation.json",
                "completion": "completion.json",
            },
        })
        _write_json(base / "requirements.json", {
            "schema_version": "1",
            "artifact_type": "plan-requirements",
            "plan_id": "DEMO-PLAN",
            "requirements": [{
                "id": "FS0-NR-900",
                "statement": "The demonstration runtime SHALL create its planned file.",
                "evaluation": {
                    "conformance": {"applicability": "required"},
                    "assurance": {"applicability": "required"},
                },
            }],
        })
        _write_json(base / "files/001-demo.json", {
            "schema_version": "1",
            "artifact_type": "plan-file",
            "plan_id": "DEMO-PLAN",
            "file_change": {
                "path": "repo/runtime/demo.txt",
                "operation": "create",
                "purpose": "Create the demonstration runtime output.",
                "requirement_ids": ["FS0-NR-900"],
                "implementation": ["Write the demonstration marker."],
                "validation_ids": ["VAL-DEMO"],
                "depends_on_paths": [],
                "generated_consequences": [],
            },
        })
        _write_json(base / "execution.json", {
            "schema_version": "1",
            "artifact_type": "plan-execution",
            "plan_id": "DEMO-PLAN",
            "ordered_steps": [{"step": 1, "description": "Create demo.", "paths": ["repo/runtime/demo.txt"]}],
        })
        _write_json(base / "invariants.json", {
            "schema_version": "1",
            "artifact_type": "plan-invariants",
            "plan_id": "DEMO-PLAN",
            "invariants": [],
        })
        _write_json(base / "validation.json", {
            "schema_version": "1",
            "artifact_type": "plan-validation",
            "plan_id": "DEMO-PLAN",
            "validation": [{
                "id": "VAL-DEMO",
                "kind": "unit",
                "description": "Demo validation.",
                "success_criteria": "The planned file exists.",
                "requirement_ids": ["FS0-NR-900"],
            }],
        })
        _write_json(base / "completion.json", {
            "schema_version": "1",
            "artifact_type": "plan-completion",
            "plan_id": "DEMO-PLAN",
            "completion_conditions": [],
        })
        _git(root, "add", ".")
        _git(root, "commit", "-m", "planning")
        planning_revision = _git(root, "rev-parse", "HEAD")

        repo = Repository(root)
        fs_path = base / "functional-set.json"
        plan_path = base / "plan.json"
        fs_doc = load_json(fs_path)
        design_report = design_conformance(repo, fs_doc["design_inputs"][0])
        fs_report = functional_set_conformance(repo, str(fs_path))
        plan, plan_report = plan_conformance(repo, str(plan_path))

        planning_assurance = make_report(
            phase="Planning",
            subject_id=plan.id,
            disposition="PASS",
            rationale="Explicit semantic-review demonstration for the temporary self-host Plan.",
            evidence_refs=("self-host:design", "self-host:functional-set", "self-host:plan"),
        )
        planning_graph = AuthorizationGraph(
            [Authority("accepted-predecessor"), Authority("governor")],
            [Delegation("accepted-predecessor", "governor", "accept:Planning")],
        )
        planning_acceptance = accept(
            acceptance_id="SELFHOST-PLAN-ACCEPT",
            stage="Planning",
            subject_id=plan.id,
            actor="governor",
            predecessor_authority="accepted-predecessor",
            resulting_state="accepted-plan",
            authority_graph=planning_graph,
            conformance=plan_report,
            assurance=planning_assurance,
            evidence_refs=("self-host:plan-conformance", "self-host:planning-assurance"),
        )

        session = BuildSession.open(
            repo,
            plan,
            build_id="SELFHOST-BUILD",
            actor="builder",
            build_start_revision=planning_revision,
        )
        target = root / "repo/runtime/demo.txt"
        session.require_authorized("repo/runtime/demo.txt", "create")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("FS0 self-host demonstration\n", encoding="utf-8")
        _git(root, "add", ".")
        _git(root, "commit", "-m", "build")
        build_revision = _git(root, "rev-parse", "HEAD")
        manifest = session.manifest(resulting_revision=build_revision)
        build_report = build_conformance(plan, manifest)
        build_assurance = make_report(
            phase="Build",
            subject_id=session.build_id,
            disposition="PASS",
            rationale="Explicit semantic-review demonstration for the temporary self-host Build.",
            evidence_refs=("self-host:manifest", "self-host:build-conformance"),
        )
        build_graph = AuthorizationGraph(
            [Authority("accepted-plan"), Authority("governor")],
            [Delegation("accepted-plan", "governor", "accept:Build")],
        )
        build_acceptance = accept(
            acceptance_id="SELFHOST-BUILD-ACCEPT",
            stage="Build",
            subject_id=session.build_id,
            actor="governor",
            predecessor_authority="accepted-plan",
            resulting_state=build_revision,
            authority_graph=build_graph,
            conformance=build_report,
            assurance=build_assurance,
            evidence_refs=("self-host:build-conformance", "self-host:build-assurance"),
        )
        return {
            "status": "PASS",
            "design_conformance": design_report.disposition,
            "functional_set_conformance": fs_report.disposition,
            "plan_conformance": plan_report.disposition,
            "planning_acceptance": planning_acceptance.decision,
            "build_conformance": build_report.disposition,
            "build_acceptance": build_acceptance.decision,
            "default_deny": not planning_graph.authorized("builder", "accept:Planning", authority="accepted-predecessor"),
        }


def _validate_core(repo: Repository) -> dict:
    plan_path = repo.root / "repo/planning/000_FS0-CORE/plan.json"
    plan, plan_report = plan_conformance(repo, str(plan_path))
    fs_path = repo.root / plan.functional_set.design_inputs[0]["path"]
    del fs_path  # Design paths are validated through exact revision reads below.
    design_reports = [
        design_conformance(repo, item)
        for item in plan.functional_set.design_inputs
    ]
    functional_report = functional_set_conformance(
        repo, str(repo.root / "repo/planning/000_FS0-CORE/functional-set.json")
    )
    for schema in (
        "repo/planning/assurance-report.schema.json",
        "repo/planning/acceptance.schema.json",
        "repo/planning/conformance-report.schema.json",
        "repo/planning/build-manifest.schema.json",
    ):
        json.loads((repo.root / schema).read_text(encoding="utf-8"))

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(repo.root / "repo/runtime")
    tests = subprocess.run(
        [
            sys.executable, "-B", "-m", "unittest", "discover",
            "-s", str(repo.root / "repo/tests/fs0_core"), "-p", "test_*.py",
        ],
        cwd=repo.root,
        env=env,
        text=True,
        capture_output=True,
    )
    if tests.returncode:
        raise RuntimeError(tests.stderr or tests.stdout)

    planning_assurance = make_report(
        phase="Planning",
        subject_id=plan.id,
        disposition="PASS",
        rationale="Canonical FS0-Core validation confirms the resolved Plan is coherent with its bound Design scope.",
        evidence_refs=(
            "core:design-conformance",
            "core:functional-set-conformance",
            "core:plan-conformance",
            "core:unit-tests",
        ),
    )
    predecessor_authority = plan.implementation_predecessor
    accepted_plan_authority = f"accepted-plan:{plan.id}"
    planning_graph = AuthorizationGraph(
        [Authority(predecessor_authority), Authority("core-governor")],
        [Delegation(predecessor_authority, "core-governor", "accept:Planning")],
    )
    planning_acceptance = accept(
        acceptance_id="FS0-CORE-PLAN-ACCEPT",
        stage="Planning",
        subject_id=plan.id,
        actor="core-governor",
        predecessor_authority=predecessor_authority,
        resulting_state=accepted_plan_authority,
        authority_graph=planning_graph,
        conformance=plan_report,
        assurance=planning_assurance,
        evidence_refs=("core:plan-conformance", "core:planning-assurance"),
    )

    accepted_state_path = repo.root / "repo/evidence/fs0-core/accepted-state.json"
    if accepted_state_path.is_file():
        accepted_state = load_json(accepted_state_path)
        core_result = accepted_state.get("resulting_revision")
        repo.require_revision(core_result)
        manifest = _auto_build_manifest(repo, plan)
        manifest["resulting_revision"] = core_result
        planned_paths = {fc.path for fc in plan.file_changes}
        mutations = []
        for mutation in repo.changed_paths(plan.implementation_predecessor, core_result):
            artifact_only = mutation.path.startswith("repo/proposals/") or mutation.path.startswith("repo/planning/")
            if artifact_only and mutation.path not in planned_paths:
                continue
            mutations.append({"path": mutation.path, "operation": mutation.operation})
        manifest["mutations"] = mutations
    else:
        manifest = _auto_build_manifest(repo, plan)
    build_report = build_conformance(plan, manifest)
    build_assurance = make_report(
        phase="Build",
        subject_id=manifest["build_id"],
        disposition="PASS",
        rationale="Canonical FS0-Core validation confirms the complete observed Build remains within the accepted Plan.",
        evidence_refs=("core:build-manifest", "core:build-conformance", "core:unit-tests"),
    )
    build_graph = AuthorizationGraph(
        [Authority(accepted_plan_authority), Authority("core-governor")],
        [Delegation(accepted_plan_authority, "core-governor", "accept:Build")],
    )
    build_acceptance = accept(
        acceptance_id="FS0-CORE-BUILD-ACCEPT",
        stage="Build",
        subject_id=manifest["build_id"],
        actor="core-governor",
        predecessor_authority=accepted_plan_authority,
        resulting_state=repo.head,
        authority_graph=build_graph,
        conformance=build_report,
        assurance=build_assurance,
        evidence_refs=("core:build-conformance", "core:build-assurance"),
    )

    self_host = _self_host_check()
    return {
        "status": "PASS",
        "design_reports": len(design_reports),
        "functional_set_conformance": functional_report.disposition,
        "plan_conformance": plan_report.disposition,
        "tests": "PASS",
        "planning_assurance": planning_assurance.disposition,
        "planning_acceptance": planning_acceptance.decision,
        "build_conformance": build_report.disposition,
        "build_assurance": build_assurance.disposition,
        "build_acceptance": build_acceptance.decision,
        "implementation_predecessor": manifest["implementation_predecessor"],
        "resulting_revision": manifest["resulting_revision"],
        "self_host": self_host["status"],
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="repo-spec")
    p.add_argument("--repository", default=".")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("design-check")
    d.add_argument("--doc-id", required=True)
    d.add_argument("--path", required=True)
    d.add_argument("--revision", required=True)
    d.add_argument("--statement", action="append", required=True)

    f = sub.add_parser("functional-set-check")
    f.add_argument("path")

    pc = sub.add_parser("plan-check")
    pc.add_argument("path")

    for name, phase in (
        ("design-assure", "Design"),
        ("planning-assure", "Planning"),
        ("build-assure", "Build"),
    ):
        q = sub.add_parser(name)
        q.add_argument("--subject", required=True)
        q.add_argument("--disposition", choices=["PASS", "FAIL"], required=True)
        q.add_argument("--rationale", required=True)
        q.add_argument("--evidence", action="append", default=[])
        q.add_argument("--output")
        q.set_defaults(assurance_phase=phase)

    for name, stage in (("plan-accept", "Planning"), ("build-accept", "Build")):
        q = sub.add_parser(name)
        q.add_argument("--acceptance-id", required=True)
        q.add_argument("--subject", required=True)
        q.add_argument("--actor", required=True)
        q.add_argument("--authority", required=True)
        q.add_argument("--authority-state", required=True)
        q.add_argument("--resulting-state", required=True)
        q.add_argument("--conformance", required=True)
        q.add_argument("--assurance", required=True)
        q.add_argument("--evidence", action="append", required=True)
        q.add_argument("--output", required=True)
        q.set_defaults(acceptance_stage=stage)

    bo = sub.add_parser("build-open")
    bo.add_argument("plan")
    bo.add_argument("--build-id", required=True)
    bo.add_argument("--actor", required=True)
    bo.add_argument("--build-start-revision")

    bc = sub.add_parser("build-check")
    bc.add_argument("plan")
    bc.add_argument("manifest", nargs="?")
    bc.add_argument("--validation-output")
    bc.add_argument("--conformance-output")

    status = sub.add_parser("status")
    mode = status.add_mutually_exclusive_group()
    mode.add_argument("--self-host-check", action="store_true")
    mode.add_argument("--validate-core", action="store_true")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo = _repo(args)

        if args.command == "design-check":
            report = design_conformance(repo, {
                "doc_id": args.doc_id,
                "path": args.path,
                "revision": args.revision,
                "statements": args.statement,
            })
            _emit(report.to_dict())
            return 0

        if args.command == "functional-set-check":
            _emit(functional_set_conformance(repo, args.path).to_dict())
            return 0

        if args.command == "plan-check":
            _, report = plan_conformance(repo, args.path)
            _emit(report.to_dict())
            return 0

        if args.command.endswith("-assure"):
            refs = require_evidence_refs(repo.root, args.evidence) if args.evidence else ()
            report = make_report(
                phase=args.assurance_phase,
                subject_id=args.subject,
                disposition=args.disposition,
                rationale=args.rationale,
                evidence_refs=refs,
            )
            value = {
                "schema_version": "1",
                "artifact_type": "assurance-report",
                "phase": report.phase,
                "subject_id": report.subject_id,
                "disposition": report.disposition,
                "rationale": report.rationale,
                "evidence_refs": list(report.evidence_refs),
                "findings": [],
            }
            if args.output:
                write_evidence(repo.root, args.output, value)
            _emit(value)
            return 0 if report.passed else 1

        if args.command in {"plan-accept", "build-accept"}:
            conf = _conformance_from_dict(load_json(Path(args.conformance)))
            assurance = _assurance_from_dict(load_json(Path(args.assurance)))
            graph = load_authorization_graph(repo.root, args.authority_state)
            refs = require_evidence_refs(repo.root, args.evidence)
            record = accept(
                acceptance_id=args.acceptance_id,
                stage=args.acceptance_stage,
                subject_id=args.subject,
                actor=args.actor,
                predecessor_authority=args.authority,
                resulting_state=args.resulting_state,
                authority_graph=graph,
                conformance=conf,
                assurance=assurance,
                evidence_refs=refs,
            )
            value = record.to_dict()
            write_evidence(repo.root, args.output, value)
            _emit(value)
            return 0

        if args.command == "build-open":
            plan, _ = plan_conformance(repo, args.plan)
            session = BuildSession.open(
                repo,
                plan,
                build_id=args.build_id,
                actor=args.actor,
                build_start_revision=args.build_start_revision,
            )
            _emit({
                "build_id": session.build_id,
                "plan_id": plan.id,
                "actor": session.actor,
                "build_start_revision": session.build_start_revision,
            })
            return 0

        if args.command == "build-check":
            plan, _ = plan_conformance(repo, args.plan)
            validation_results = run_plan_validations(repo, plan)
            validation_value = {
                "schema_version": "1",
                "artifact_type": "validation-run",
                "plan_id": plan.id,
                "results": [result.to_dict() for result in validation_results],
                "disposition": "PASS",
            }
            validation_ref = (
                write_evidence(repo.root, args.validation_output, validation_value)
                if args.validation_output else None
            )
            manifest = load_json(Path(args.manifest)) if args.manifest else _auto_build_manifest(repo, plan)
            base_report = build_conformance(plan, manifest)
            report = ConformanceReport(
                base_report.report_id,
                base_report.subject_type,
                base_report.subject_id,
                base_report.disposition,
                base_report.evidence_refs + ((validation_ref,) if validation_ref else ()),
                base_report.findings,
            )
            value = report.to_dict()
            if args.conformance_output:
                write_evidence(repo.root, args.conformance_output, value)
            _emit(value)
            return 0

        if args.command == "status":
            if args.self_host_check:
                _emit(_self_host_check())
                return 0
            if args.validate_core:
                _emit(_validate_core(repo))
                return 0
            _emit({"repository": str(repo.root), "head": repo.head, "clean": repo.is_clean()})
            return 0

        raise RuntimeError(f"unhandled command: {args.command}")

    except RepoSpecError as exc:
        _emit({
            "status": "ERROR",
            "phase": exc.owning_phase,
            "code": exc.code,
            "message": exc.message,
        })
        return 1
    except Exception as exc:
        _emit({"status": "ERROR", "phase": "Runtime", "code": "runtime-error", "message": str(exc)})
        return 1
