from __future__ import annotations

import json
from pathlib import Path


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


RUNNER = '#!/usr/bin/env python3\nfrom __future__ import annotations\n\nimport json\nimport subprocess\nimport sys\nfrom pathlib import Path\n\n\ndef load(path: Path):\n    return json.loads(path.read_text(encoding="utf-8"))\n\n\ndef result(assertion_id, status, detail, evidence=None):\n    rec = {"assertion_id": assertion_id, "status": status, "detail": detail}\n    if evidence is not None:\n        rec["evidence"] = evidence\n    return rec\n\n\ndef check_requirement_metadata(root, assertion_ids):\n    reqs = load(root / "repo/authority/requirements.json")["requirements"]\n    ids = [r["requirement_id"] for r in reqs]\n    checks = {\n        "FS0-ASSERT-FC-045": (len(reqs) == 164 and len(ids) == len(set(ids)) and all(ids), "requirement identities are present and unique"),\n        "FS0-ASSERT-FC-056": (all(r.get("lifecycle_state") in {"accepted", "superseded", "withdrawn"} for r in reqs), "requirement lifecycle states use the allowed enumeration"),\n        "FS0-ASSERT-FC-057": (all(r.get("conformance_applicability") in {"mechanical", "none"} for r in reqs), "Conformance applicability uses mechanical|none"),\n        "FS0-ASSERT-FC-058": (all(r.get("assurance_applicability") in {"required", "none"} for r in reqs), "Assurance applicability uses required|none"),\n        "FS0-ASSERT-FC-075": (all(len(r.get("statement", "")) <= 300 for r in reqs), "all normative requirement statements are <=300 characters"),\n        "FS0-ASSERT-CONF-024": (all(len(r.get("statement", "")) <= 300 for r in reqs), "Conformance rejects the present state if a requirement exceeds 300 characters"),\n    }\n    return [result(aid, "pass" if checks[aid][0] else "fail", checks[aid][1]) for aid in assertion_ids]\n\n\ndef check_conformance_closure(root, assertion_ids):\n    reqs = load(root / "repo/authority/requirements.json")["requirements"]\n    corr = load(root / "repo/conformance/correspondence.json")["records"]\n    assertions = load(root / "repo/conformance/assertions.json")["assertions"]\n    impl = load(root / "repo/conformance/support/implementations.json")["implementations"]\n\n    req_ids = [r["requirement_id"] for r in reqs]\n    corr_by_req = {r["requirement_id"]: r for r in corr}\n    assertion_by_id = {a["assertion_id"]: a for a in assertions}\n    implementation_ids = {i["implementation_id"] for i in impl}\n\n    checks = {\n        "FS0-ASSERT-CONF-001": (len(corr) == len(reqs) == 164 and set(corr_by_req) == set(req_ids), "every requirement has exactly one Conformance correspondence"),\n        "FS0-ASSERT-CONF-004": (all(a["assertion_id"] not in implementation_ids for a in assertions), "assertion identities are distinct from implementation identities"),\n        "FS0-ASSERT-CONF-013": (all({"requirement_id", "applicability", "assertion_ids"} <= set(r) for r in corr), "all correspondence records contain required fields"),\n        "FS0-ASSERT-CONF-015": (len({a["assertion_id"] for a in assertions}) == len(assertions) and all(a.get("requirement_id") for a in assertions), "shared implementations preserve distinct assertion identity and provenance"),\n        "FS0-ASSERT-CONF-018": (all(r["assertion_ids"] and all(aid in assertion_by_id for aid in r["assertion_ids"]) for r in corr if r["applicability"] == "mechanical"), "mechanical correspondence records contain stable assertion identities"),\n        "FS0-ASSERT-CONF-019": (all(not r["assertion_ids"] for r in corr if r["applicability"] == "none"), "none-applicable correspondence records contain empty assertion_ids"),\n    }\n    return [result(aid, "pass" if checks[aid][0] else "fail", checks[aid][1]) for aid in assertion_ids]\n\n\ndef check_generation_correspondence(root, assertion_ids):\n    proc = subprocess.run([str(root / "repo/bootstrap/scripts/bootstrap"), "--check"], cwd=root, text=True, capture_output=True)\n    ok = proc.returncode == 0 and "FS0 generation correspondence: PASS" in proc.stdout\n    evidence = {"returncode": proc.returncode, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}\n    out = []\n    for aid in assertion_ids:\n        detail = "deterministic regeneration matches checked-in generated surfaces" if aid == "FS0-ASSERT-CONF-022" else "generation-correspondence failure is surfaced as a Conformance defect"\n        out.append(result(aid, "pass" if ok else "fail", detail, evidence))\n    return out\n\n\ndef check_canonical_entrypoint(root, assertion_ids):\n    engine = root / "repo/conformance/run.py"\n    wrapper = root / "repo/scripts/validate"\n    ok = engine.is_file() and wrapper.is_file()\n    return [result(aid, "pass" if ok else "fail", "repo/conformance/run.py exists as the canonical Conformance engine and repo/scripts/validate exposes it", {"entrypoint": "repo/conformance/run.py", "wrapper": "repo/scripts/validate"}) for aid in assertion_ids]\n\n\nCALLABLES = {\n    "requirement_metadata": check_requirement_metadata,\n    "conformance_closure": check_conformance_closure,\n    "generation_correspondence": check_generation_correspondence,\n    "canonical_entrypoint": check_canonical_entrypoint,\n}\n\n\ndef main():\n    root = Path.cwd().resolve()\n    if not (root / ".git").exists():\n        print("run from repository root", file=sys.stderr)\n        return 2\n\n    implementations = load(root / "repo/conformance/support/implementations.json")["implementations"]\n    orchestration = load(root / "repo/conformance/orchestration.json")\n    all_assertions = load(root / "repo/conformance/assertions.json")["assertions"]\n    mechanical_ids = {a["assertion_id"] for a in all_assertions}\n\n    realized = set()\n    results = []\n    for impl in implementations:\n        callable_name = impl["callable"]\n        assertion_ids = impl["assertion_ids"]\n        realized.update(assertion_ids)\n        fn = CALLABLES.get(callable_name)\n        if fn is None:\n            results.extend(result(aid, "fail", f"unknown implementation callable: {callable_name}") for aid in assertion_ids)\n            continue\n        results.extend(fn(root, assertion_ids))\n\n    pending = sorted(mechanical_ids - realized)\n    failed = sorted(r["assertion_id"] for r in results if r["status"] == "fail")\n    passed = sorted(r["assertion_id"] for r in results if r["status"] == "pass")\n    status = "fail" if failed else ("incomplete" if pending else "pass")\n\n    report = {\n        "schema_version": "1",\n        "record_type": "conformance-execution-result",\n        "orchestration_id": orchestration["orchestration_id"],\n        "status": status,\n        "realized_assertions": len(realized),\n        "passed_assertions": len(passed),\n        "failed_assertions": failed,\n        "pending_assertions": pending,\n        "results": results,\n    }\n    print(json.dumps(report, indent=2))\n\n    if failed:\n        return 1\n    if pending:\n        return 2\n    return 0\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n'
VALIDATE = '#!/usr/bin/env python3\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport subprocess\nimport sys\nfrom pathlib import Path\n\n\ndef repository_root() -> Path:\n    root = Path.cwd().resolve()\n    if not (root / ".git").exists() or not (root / "repo/conformance/run.py").is_file():\n        print("repo/scripts/validate must be invoked from repository root", file=sys.stderr)\n        raise SystemExit(2)\n    return root\n\n\ndef run_engine(root: Path):\n    proc = subprocess.run(\n        [sys.executable, str(root / "repo/conformance/run.py")],\n        cwd=root,\n        text=True,\n        capture_output=True,\n    )\n    if proc.stderr:\n        print(proc.stderr, end="", file=sys.stderr)\n    try:\n        report = json.loads(proc.stdout)\n    except json.JSONDecodeError:\n        if proc.stdout:\n            print(proc.stdout, end="")\n        print("Conformance engine did not produce a valid structured result", file=sys.stderr)\n        raise SystemExit(proc.returncode if proc.returncode else 1)\n    return proc.returncode, report, proc.stdout\n\n\ndef status_label(report):\n    status = report.get("status")\n    return {\n        "pass": "PASS",\n        "fail": "FAILED",\n        "incomplete": "INCOMPLETE",\n    }.get(status, str(status).upper())\n\n\ndef counts(report):\n    passed = int(report.get("passed_assertions", 0))\n    failed = len(report.get("failed_assertions", []))\n    pending = len(report.get("pending_assertions", []))\n    return passed, failed, pending\n\n\ndef print_summary(report):\n    passed, failed, pending = counts(report)\n    print(f"FS0 Conformance: {status_label(report)}")\n    print()\n    print(f"Passed:  {passed}")\n    print(f"Failed:  {failed}")\n    print(f"Pending: {pending}")\n\n    failed_ids = report.get("failed_assertions", [])\n    result_by_id = {r.get("assertion_id"): r for r in report.get("results", [])}\n\n    if failed_ids:\n        print()\n        print("Failed assertions:")\n        for aid in failed_ids:\n            item = result_by_id.get(aid, {})\n            print(f"  {aid}")\n            detail = item.get("detail")\n            if detail:\n                print(f"    {detail}")\n    elif pending:\n        print()\n        print("No realized assertions failed.")\n\n    if failed_ids or pending:\n        print()\n        print("Run:")\n        print("  repo/scripts/validate --verbose   show assertion details")\n        print("  repo/scripts/validate --json      emit full structured result")\n\n\ndef print_verbose(report):\n    print_summary(report)\n\n    results = report.get("results", [])\n    pending = report.get("pending_assertions", [])\n\n    if results:\n        print()\n        print("Realized assertions:")\n        for item in results:\n            aid = item.get("assertion_id", "<unknown>")\n            state = str(item.get("status", "unknown")).upper()\n            print(f"  [{state}] {aid}")\n            detail = item.get("detail")\n            if detail:\n                print(f"         {detail}")\n\n    if pending:\n        print()\n        print("Pending assertions:")\n        for aid in pending:\n            print(f"  [PENDING] {aid}")\n\n\ndef main():\n    parser = argparse.ArgumentParser(\n        prog="repo/scripts/validate",\n        description="Run FS0 Conformance validation.",\n    )\n    group = parser.add_mutually_exclusive_group()\n    group.add_argument(\n        "--verbose",\n        action="store_true",\n        help="show realized and pending assertion details",\n    )\n    group.add_argument(\n        "--json",\n        action="store_true",\n        help="emit the complete structured Conformance result",\n    )\n    args = parser.parse_args()\n\n    root = repository_root()\n    code, report, raw = run_engine(root)\n\n    if args.json:\n        print(raw, end="" if raw.endswith("\\n") else "\\n")\n    elif args.verbose:\n        print_verbose(report)\n    else:\n        print_summary(report)\n\n    return code\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n'


def derive_conformance_realization(root: Path, requirements, assertions):
    data_path = root / "repo/bootstrap/data/realization/conformance.json"
    data = _load(data_path)

    if data.get("schema_version") != "1":
        raise SystemExit("unsupported Conformance realization data schema")
    if data.get("record_type") != "conformance-realization-data":
        raise SystemExit("unexpected Conformance realization data record_type")

    assertion_by_id = {a["assertion_id"]: a for a in assertions}
    mechanical_requirement_ids = {
        r["requirement_id"]
        for r in requirements
        if r["conformance_applicability"] == "mechanical"
    }

    seen_impl = set()
    seen_assertions = set()
    implementations = []
    for impl in data.get("implementations", []):
        iid = impl.get("implementation_id")
        callable_name = impl.get("callable")
        aids = impl.get("assertion_ids")
        if not iid or iid in seen_impl:
            raise SystemExit(f"invalid or duplicate implementation identity: {iid}")
        if not callable_name or not isinstance(aids, list) or not aids:
            raise SystemExit(f"{iid}: invalid implementation realization")
        seen_impl.add(iid)

        for aid in aids:
            if aid in seen_assertions:
                raise SystemExit(f"assertion bound more than once: {aid}")
            if aid not in assertion_by_id:
                raise SystemExit(f"{iid}: unknown assertion identity: {aid}")
            rid = assertion_by_id[aid]["requirement_id"]
            if rid not in mechanical_requirement_ids:
                raise SystemExit(f"{iid}: assertion does not resolve to a mechanical requirement: {aid}")
            seen_assertions.add(aid)

        implementations.append({
            "schema_version": "1",
            "record_type": "conformance-implementation",
            "implementation_id": iid,
            "role": "support",
            "callable": callable_name,
            "assertion_ids": aids,
        })

    evidence = data.get("evidence", [])
    evidence_ids = set()
    for item in evidence:
        eid = item.get("evidence_id")
        if not eid or eid in evidence_ids:
            raise SystemExit(f"invalid or duplicate evidence identity: {eid}")
        if item.get("implementation_id") not in seen_impl:
            raise SystemExit(f"{eid}: unknown implementation identity")
        evidence_ids.add(eid)

    orchestration = data.get("orchestration")
    if not isinstance(orchestration, dict):
        raise SystemExit("missing canonical Conformance orchestration data")
    if orchestration.get("entrypoint") != "repo/conformance/run.py":
        raise SystemExit("canonical Conformance entrypoint must be repo/conformance/run.py")
    if orchestration.get("public_wrapper") != "repo/scripts/validate":
        raise SystemExit("public Conformance wrapper must be repo/scripts/validate")

    pending = sorted(set(assertion_by_id) - seen_assertions)

    return {
        root / "repo/conformance/support/implementations.json": {
            "schema_version": "1",
            "record_type": "conformance-implementation-registry",
            "implementations": implementations,
        },
        root / "repo/conformance/evidence.json": {
            "schema_version": "1",
            "record_type": "conformance-evidence-registry",
            "evidence": evidence,
        },
        root / "repo/conformance/orchestration.json": {
            "schema_version": "1",
            "record_type": "conformance-orchestration",
            **orchestration,
            "realized_assertion_ids": sorted(seen_assertions),
            "pending_assertion_ids": pending,
        },
        root / "repo/conformance/run.py": RUNNER,
        root / "repo/scripts/validate": VALIDATE,
    }
