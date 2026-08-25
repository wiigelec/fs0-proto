"""Deterministic JSON CLI orchestration for FS0-Core."""

from __future__ import annotations
import argparse
import json
import sys

from .assurance import make_report
from .build import BuildSession
from .conformance import design_conformance, functional_set_conformance, plan_conformance, build_conformance
from .errors import RepoSpecError
from .repository import Repository

def _emit(value: dict) -> None:
    print(json.dumps(value, sort_keys=True))

def _repo(args) -> Repository:
    return Repository(args.repository)

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="repo-spec")
    p.add_argument("--repository", required=True)
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("design-check")
    d.add_argument("--doc-id", required=True); d.add_argument("--path", required=True)
    d.add_argument("--revision", required=True); d.add_argument("--statement", action="append", required=True)

    f = sub.add_parser("functional-set-check")
    f.add_argument("path")

    pc = sub.add_parser("plan-check")
    pc.add_argument("path")

    for name, phase in (("design-assure","Design"),("planning-assure","Planning"),("build-assure","Build")):
        q = sub.add_parser(name)
        q.add_argument("--subject", required=True); q.add_argument("--disposition", choices=["PASS","FAIL"], required=True)
        q.add_argument("--rationale", required=True); q.set_defaults(assurance_phase=phase)

    bo = sub.add_parser("build-open")
    bo.add_argument("plan"); bo.add_argument("--build-id", required=True); bo.add_argument("--actor", required=True)
    bo.add_argument("--build-start-revision")

    bc = sub.add_parser("build-check")
    bc.add_argument("plan"); bc.add_argument("manifest")

    sub.add_parser("status")
    return p

def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo = _repo(args)
        if args.command == "design-check":
            report = design_conformance(repo, {
                "doc_id": args.doc_id, "path": args.path, "revision": args.revision,
                "statements": args.statement,
            })
            _emit(report.to_dict()); return 0
        if args.command == "functional-set-check":
            _emit(functional_set_conformance(repo, args.path).to_dict()); return 0
        if args.command == "plan-check":
            _, report = plan_conformance(repo, args.path)
            _emit(report.to_dict()); return 0
        if args.command.endswith("-assure"):
            report = make_report(
                phase=args.assurance_phase, subject_id=args.subject,
                disposition=args.disposition, rationale=args.rationale,
            )
            _emit({
                "schema_version":"1","artifact_type":"assurance-report",
                "phase":report.phase,"subject_id":report.subject_id,
                "disposition":report.disposition,"rationale":report.rationale,
                "evidence_refs":list(report.evidence_refs),"findings":[],
            })
            return 0 if report.passed else 1
        if args.command == "build-open":
            plan, _ = plan_conformance(repo, args.plan)
            session = BuildSession.open(
                repo, plan, build_id=args.build_id, actor=args.actor,
                build_start_revision=args.build_start_revision,
            )
            _emit({
                "build_id":session.build_id,"plan_id":plan.id,"actor":session.actor,
                "build_start_revision":session.build_start_revision,
            }); return 0
        if args.command == "build-check":
            from .jsonio import load_json
            plan, _ = plan_conformance(repo, args.plan)
            report = build_conformance(plan, load_json(__import__("pathlib").Path(args.manifest)))
            _emit(report.to_dict()); return 0
        if args.command == "status":
            _emit({"repository":str(repo.root),"head":repo.head,"clean":repo.is_clean()}); return 0
        raise RuntimeError(f"unhandled command: {args.command}")
    except RepoSpecError as exc:
        _emit({"status":"ERROR","phase":exc.owning_phase,"code":exc.code,"message":exc.message})
        return 1
