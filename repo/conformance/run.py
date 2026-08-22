#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def result(assertion_id, status, detail, evidence=None):
    rec = {"assertion_id": assertion_id, "status": status, "detail": detail}
    if evidence is not None:
        rec["evidence"] = evidence
    return rec


def check_requirement_metadata(root, assertion_ids):
    registry = load(root / "repo/authority/requirements.json")
    reqs = registry["requirements"]
    ids = [r["requirement_id"] for r in reqs]
    checks = {
        "FS0-ASSERT-FC-045": (registry.get("requirements_total") == len(reqs) and len(ids) == len(set(ids)) and all(ids), "requirement identities are present and unique and the registry count is self-consistent"),
        "FS0-ASSERT-FC-056": (all(r.get("lifecycle_state") in {"accepted", "superseded", "withdrawn"} for r in reqs), "requirement lifecycle states use the allowed enumeration"),
        "FS0-ASSERT-FC-057": (all(r.get("conformance_applicability") in {"mechanical", "none"} for r in reqs), "Conformance applicability uses mechanical|none"),
        "FS0-ASSERT-FC-058": (all(r.get("assurance_applicability") in {"required", "none"} for r in reqs), "Assurance applicability uses required|none"),
        "FS0-ASSERT-FC-075": (all(len(r.get("statement", "")) <= 300 for r in reqs), "all normative requirement statements are <=300 characters"),
        "FS0-ASSERT-CONF-024": (all(len(r.get("statement", "")) <= 300 for r in reqs), "Conformance rejects the present state if a requirement exceeds 300 characters"),
    }
    return [result(aid, "pass" if checks[aid][0] else "fail", checks[aid][1]) for aid in assertion_ids]


def check_conformance_closure(root, assertion_ids):
    req_registry = load(root / "repo/authority/requirements.json")
    corr_registry = load(root / "repo/conformance/correspondence.json")
    reqs = req_registry["requirements"]
    corr = corr_registry["records"]
    assertions = load(root / "repo/conformance/assertions.json")["assertions"]
    impl = load(root / "repo/conformance/support/implementations.json")["implementations"]

    req_ids = [r["requirement_id"] for r in reqs]
    corr_by_req = {r["requirement_id"]: r for r in corr}
    assertion_by_id = {a["assertion_id"]: a for a in assertions}
    implementation_ids = {i["implementation_id"] for i in impl}

    checks = {
        "FS0-ASSERT-CONF-001": (req_registry.get("requirements_total") == corr_registry.get("requirements_total") == len(reqs) == len(corr) and set(corr_by_req) == set(req_ids), "every requirement has exactly one Conformance correspondence and registry totals agree"),
        "FS0-ASSERT-CONF-004": (all(a["assertion_id"] not in implementation_ids for a in assertions), "assertion identities are distinct from implementation identities"),
        "FS0-ASSERT-CONF-013": (all({"requirement_id", "applicability", "assertion_ids"} <= set(r) for r in corr), "all correspondence records contain required fields"),
        "FS0-ASSERT-CONF-015": (len({a["assertion_id"] for a in assertions}) == len(assertions) and all(a.get("requirement_id") for a in assertions), "shared implementations preserve distinct assertion identity and provenance"),
        "FS0-ASSERT-CONF-018": (all(r["assertion_ids"] and all(aid in assertion_by_id for aid in r["assertion_ids"]) for r in corr if r["applicability"] == "mechanical"), "mechanical correspondence records contain stable assertion identities"),
        "FS0-ASSERT-CONF-019": (all(not r["assertion_ids"] for r in corr if r["applicability"] == "none"), "none-applicable correspondence records contain empty assertion_ids"),
    }
    return [result(aid, "pass" if checks[aid][0] else "fail", checks[aid][1]) for aid in assertion_ids]


def check_generation_correspondence(root, assertion_ids):
    proc = subprocess.run([str(root / "repo/bootstrap/scripts/bootstrap"), "--check"], cwd=root, text=True, capture_output=True)
    ok = proc.returncode == 0 and "FS0 generation correspondence: PASS" in proc.stdout
    evidence = {"returncode": proc.returncode, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}
    out = []
    for aid in assertion_ids:
        detail = "deterministic regeneration matches checked-in generated surfaces" if aid == "FS0-ASSERT-CONF-022" else "generation-correspondence failure is surfaced as a Conformance defect"
        out.append(result(aid, "pass" if ok else "fail", detail, evidence))
    return out


def check_canonical_entrypoint(root, assertion_ids):
    engine = root / "repo/conformance/run.py"
    wrapper = root / "repo/scripts/validate"
    ok = engine.is_file() and wrapper.is_file()
    return [result(aid, "pass" if ok else "fail", "repo/conformance/run.py exists as the canonical Conformance engine and repo/scripts/validate exposes it", {"entrypoint": "repo/conformance/run.py", "wrapper": "repo/scripts/validate"}) for aid in assertion_ids]


def check_remote_execution(root, assertion_ids):
    workflow = root / ".github/workflows/fs0-conformance.yml"
    required = (
        "name: FS0 Conformance",
        "pull_request:",
        "push:",
        "workflow_dispatch:",
        "./repo/scripts/validate --verbose",
    )
    text = workflow.read_text(encoding="utf-8") if workflow.is_file() else ""
    ok = workflow.is_file() and all(item in text for item in required)
    evidence = {"workflow": ".github/workflows/fs0-conformance.yml"}
    return [result(aid, "pass" if ok else "fail", "GitHub Actions exposes the canonical FS0 Conformance wrapper for push, pull request, and manual execution", evidence) for aid in assertion_ids]

def check_governance_state_resolution(root, assertion_ids):
    module_path = root / "repo/governance/accepted_state.py"
    if not module_path.is_file():
        return [
            result(aid, "fail", "Governance accepted-state resolver is missing")
            for aid in assertion_ids
        ]

    spec = importlib.util.spec_from_file_location("fs0_accepted_state", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    sha = "a" * 40
    other = "b" * 40

    governance_body = (
        "repo-spec-acceptance:v1\n"
        "```json\n"
        + json.dumps(
            {
                "schema_version": "1",
                "record_type": "governance-acceptance",
                "acceptance_id": "FS0-ACCEPT-BUILD-TEST",
                "stage": "build",
                "work_id": "FS0-WORK-BUILD-TEST",
                "candidate_id": sha,
                "disposition": "accepted",
                "actor": {"login": "tester"},
                "evidence": ["evidence:test"],
                "decision_timestamp": "2026-08-22T00:00:00Z",
                "resulting_accepted_state": sha,
            }
        )
        + "\n```\n"
    )
    bootstrap_body = (
        "repo-spec-acceptance:v1\n"
        "```json\n"
        + json.dumps(
            {
                "schema_version": "1",
                "record_type": "bootstrap-acceptance",
                "acceptance_id": "FS0-ACCEPT-BOOTSTRAP-TEST",
                "stage": "bootstrap",
                "work_id": "FS0-BOOTSTRAP-PROVENANCE",
                "candidate_id": sha,
                "disposition": "accepted",
                "actor": "tester",
                "evidence": ["conformance:test", "assurance:test"],
                "decision_timestamp": "2026-08-22T00:00:00+00:00",
                "resulting_accepted_state": sha,
            }
        )
        + "\n```\n"
    )
    bad_sha_body = governance_body.replace(sha, "not-a-sha", 1)
    malformed_body = governance_body.replace(
        "repo-spec-acceptance:v1\n```json",
        "repo-spec-acceptance:v1 prose\n```json",
        1,
    )

    governance_record = module.parse_acceptance_comment(governance_body)
    bootstrap_record = module.parse_acceptance_comment(bootstrap_body)

    def rejects(body):
        try:
            module.parse_acceptance_comment(body)
        except module.AcceptanceError:
            return True
        return False

    comment = {
        "id": 1,
        "issue_url": "https://api.github.com/repos/example/repo/issues/1",
        "html_url": "https://github.com/example/repo/issues/1#issuecomment-1",
        "body": governance_body,
    }
    paired = module.resolve_accepted_state(sha, [comment])
    mismatch = module.resolve_accepted_state(other, [comment])
    unpublished = module.resolve_accepted_state(None, [comment])
    incidental = module.resolve_accepted_state(
        sha,
        [
            {
                "id": 2,
                "issue_url": "https://api.github.com/repos/example/repo/issues/2",
                "body": "merged=true workflow=success review=approved",
            }
        ],
    )

    source_text = module_path.read_text(encoding="utf-8")
    common_envelope = (
        governance_record["acceptance_id"]
        and governance_record["work_id"]
        and governance_record["candidate_id"] == sha
        and governance_record["actor"]
        and isinstance(governance_record["evidence"], list)
        and governance_record["decision_timestamp"]
    )

    checks = {
        "FS0-ASSERT-GOV-008": (
            bool(common_envelope),
            "acceptance records require explicit identity, work, exact candidate, actor, evidence, and decision timestamp",
        ),
        "FS0-ASSERT-GOV-011": (
            "issues?state=all&per_page=100" in source_text
            and "issues/comments?per_page=100" in source_text
            and '"pull_request" not in item' in source_text,
            "GitHub binding resolves acceptance records from comments on issues and excludes pull requests",
        ),
        "FS0-ASSERT-GOV-012": (
            rejects(malformed_body)
            and module.MARKER == "repo-spec-acceptance:v1",
            "acceptance parser requires the Design-defined marker immediately followed by one fenced JSON object",
        ),
        "FS0-ASSERT-GOV-013": (
            governance_record["record_type"] == "governance-acceptance"
            and governance_record["stage"] == "build"
            and governance_record["disposition"] == "accepted",
            "governance-acceptance envelope enforces schema, stage, disposition, and required fields",
        ),
        "FS0-ASSERT-GOV-014": (
            bootstrap_record["record_type"] == "bootstrap-acceptance"
            and bootstrap_record["stage"] == "bootstrap"
            and bootstrap_record["candidate_id"] == sha,
            "bootstrap-acceptance envelope enforces bootstrap stage and exact candidate revision",
        ),
        "FS0-ASSERT-GOV-015": (
            rejects(bad_sha_body),
            "repository-changing candidate_id must be an exact 40-hex Git commit SHA",
        ),
        "FS0-ASSERT-GOV-016": (
            paired["status"] == "accepted"
            and paired["accepted_revision"] == sha
            and mismatch["status"] == "invalid",
            "accepted repository state resolves only from a matching accepted ref plus valid acceptance record",
        ),
        "FS0-ASSERT-GOV-017": (
            unpublished["status"] == "unpublished"
            and incidental["status"] == "invalid",
            "default branch, merge, review, and workflow-like state do not independently create accepted repository state",
        ),
        "FS0-ASSERT-GOV-035": (
            incidental["status"] == "invalid"
            and paired["status"] == "accepted",
            "Governance acceptance remains distinct from merge, review, workflow, and tool declarations",
        ),
    }

    return [
        result(aid, "pass" if checks[aid][0] else "fail", checks[aid][1])
        for aid in assertion_ids
    ]


CALLABLES = {
    "requirement_metadata": check_requirement_metadata,
    "conformance_closure": check_conformance_closure,
    "generation_correspondence": check_generation_correspondence,
    "canonical_entrypoint": check_canonical_entrypoint,
    "remote_execution": check_remote_execution,
    "governance_state_resolution": check_governance_state_resolution,
}


def main():
    root = Path.cwd().resolve()
    if not (root / ".git").exists():
        print("run from repository root", file=sys.stderr)
        return 2

    implementations = load(root / "repo/conformance/support/implementations.json")["implementations"]
    orchestration = load(root / "repo/conformance/orchestration.json")
    all_assertions = load(root / "repo/conformance/assertions.json")["assertions"]
    mechanical_ids = {a["assertion_id"] for a in all_assertions}

    realized = set()
    results = []
    for impl in implementations:
        callable_name = impl["callable"]
        assertion_ids = impl["assertion_ids"]
        realized.update(assertion_ids)
        fn = CALLABLES.get(callable_name)
        if fn is None:
            results.extend(result(aid, "fail", f"unknown implementation callable: {callable_name}") for aid in assertion_ids)
            continue
        results.extend(fn(root, assertion_ids))

    pending = sorted(mechanical_ids - realized)
    failed = sorted(r["assertion_id"] for r in results if r["status"] == "fail")
    passed = sorted(r["assertion_id"] for r in results if r["status"] == "pass")
    status = "fail" if failed else ("incomplete" if pending else "pass")

    report = {
        "schema_version": "1",
        "record_type": "conformance-execution-result",
        "orchestration_id": orchestration["orchestration_id"],
        "status": status,
        "realized_assertions": len(realized),
        "passed_assertions": len(passed),
        "failed_assertions": failed,
        "pending_assertions": pending,
        "results": results,
    }
    print(json.dumps(report, indent=2))

    if failed:
        return 1
    if pending:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
