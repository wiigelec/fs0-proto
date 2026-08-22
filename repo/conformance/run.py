#!/usr/bin/env python3
from __future__ import annotations

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


CALLABLES = {
    "requirement_metadata": check_requirement_metadata,
    "conformance_closure": check_conformance_closure,
    "generation_correspondence": check_generation_correspondence,
    "canonical_entrypoint": check_canonical_entrypoint,
    "remote_execution": check_remote_execution,
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
