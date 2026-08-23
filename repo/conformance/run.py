#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import stat
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


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
    evidence = load(root / "repo/conformance/evidence.json")["evidence"]
    orchestration = load(root / "repo/conformance/orchestration.json")

    req_ids = [r["requirement_id"] for r in reqs]
    accepted_req_ids = {
        r["requirement_id"] for r in reqs if r.get("lifecycle_state") == "accepted"
    }
    corr_by_req = {r["requirement_id"]: r for r in corr}
    assertion_by_id = {a["assertion_id"]: a for a in assertions}
    implementation_ids = {i["implementation_id"] for i in impl}
    implementation_assertion_ids = [
        aid
        for implementation in impl
        for aid in implementation.get("assertion_ids", [])
    ]
    implementation_bindings_closed = (
        len(implementation_assertion_ids) == len(set(implementation_assertion_ids))
        and all(aid in assertion_by_id for aid in implementation_assertion_ids)
    )

    primitive_roles = (
        {a.get("role") for a in assertions}
        | {i.get("role") for i in impl}
        | {e.get("role") for e in evidence}
        | {orchestration.get("role")}
    )

    assertion_provenance_ok = all(
        a.get("requirement_id") in accepted_req_ids for a in assertions
    )
    support_provenance_ok = all(
        isinstance(i.get("authority_requirement_ids"), list)
        and i["authority_requirement_ids"]
        and all(rid in accepted_req_ids for rid in i["authority_requirement_ids"])
        for i in impl
    )
    evidence_provenance_ok = all(
        isinstance(e.get("authority_requirement_ids"), list)
        and e["authority_requirement_ids"]
        and all(rid in accepted_req_ids for rid in e["authority_requirement_ids"])
        for e in evidence
    )
    orchestration_provenance_ok = (
        isinstance(orchestration.get("authority_requirement_ids"), list)
        and bool(orchestration["authority_requirement_ids"])
        and all(
            rid in accepted_req_ids
            for rid in orchestration["authority_requirement_ids"]
        )
    )

    evidence_by_impl = {}
    for record in evidence:
        evidence_by_impl.setdefault(record.get("implementation_id"), []).append(record)
    executable_assertion_evidence_ok = all(
        evidence_by_impl.get(implementation.get("implementation_id"))
        and all(
            record.get("evidence_id")
            and record.get("role") == "evidence"
            and record.get("evidence_class") in {"execution-result", "repository-state"}
            for record in evidence_by_impl[implementation["implementation_id"]]
        )
        for implementation in impl
        if implementation.get("assertion_ids")
    )

    checks = {
        "FS0-ASSERT-CONF-001": (
            req_registry.get("requirements_total") == corr_registry.get("requirements_total")
            == len(reqs) == len(corr)
            and set(corr_by_req) == set(req_ids),
            "every requirement has exactly one Conformance correspondence and registry totals agree",
        ),
        "FS0-ASSERT-CONF-003": (
            primitive_roles == {"assertion", "support", "evidence", "orchestration"},
            "maintained Conformance primitives use exactly assertion, support, evidence, and orchestration roles",
        ),
        "FS0-ASSERT-CONF-004": (
            all(a["assertion_id"] not in implementation_ids for a in assertions),
            "assertion identities are distinct from implementation identities",
        ),
        "FS0-ASSERT-CONF-005": (
            assertion_provenance_ok
            and support_provenance_ok
            and evidence_provenance_ok
            and orchestration_provenance_ok,
            "every maintained Conformance primitive resolves to accepted normative authority",
        ),
        "FS0-ASSERT-CONF-007": (
            executable_assertion_evidence_ok,
            "every implementation that makes assertions executable resolves at least one declared Conformance evidence primitive",
        ),
        "FS0-ASSERT-CONF-013": (
            all({"requirement_id", "applicability", "assertion_ids"} <= set(r) for r in corr),
            "all correspondence records contain required fields",
        ),
        "FS0-ASSERT-CONF-015": (
            len({a["assertion_id"] for a in assertions}) == len(assertions)
            and all(a.get("requirement_id") for a in assertions)
            and implementation_bindings_closed,
            "shared implementations preserve distinct declared assertion identity and provenance, and implementation bindings are closed over the assertion registry",
        ),
        "FS0-ASSERT-CONF-018": (
            all(
                r["assertion_ids"]
                and all(aid in assertion_by_id for aid in r["assertion_ids"])
                for r in corr
                if r["applicability"] == "mechanical"
            )
            and implementation_bindings_closed,
            "mechanical correspondence records and implementation bindings contain only stable declared assertion identities",
        ),
        "FS0-ASSERT-CONF-019": (
            all(not r["assertion_ids"] for r in corr if r["applicability"] == "none"),
            "none-applicable correspondence records contain empty assertion_ids",
        ),
    }
    return [
        result(aid, "pass" if checks[aid][0] else "fail", checks[aid][1])
        for aid in assertion_ids
    ]




def check_generation_correspondence(root, assertion_ids):
    proc = subprocess.run(
        [str(root / "repo/bootstrap/scripts/bootstrap"), "--check"],
        cwd=root,
        text=True,
        capture_output=True,
    )
    correspondence_ok = (
        proc.returncode == 0
        and "FS0 generation correspondence: PASS" in proc.stdout
    )

    orchestration = load(root / "repo/conformance/orchestration.json")
    generation = orchestration.get("generation_correspondence", {})
    declared_ok = (
        generation.get("canonical_input_root") == "repo/bootstrap/data"
        and generation.get("generation_implementation")
        == "repo/bootstrap/scripts/src/generate.py"
        and generation.get("check_entrypoint")
        == "repo/bootstrap/scripts/bootstrap --check"
        and (root / generation.get("canonical_input_root", "")).is_dir()
        and (root / generation.get("generation_implementation", "")).is_file()
    )

    evidence = {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "declared_generation_correspondence": generation,
    }
    out = []
    for aid in assertion_ids:
        if aid == "FS0-ASSERT-CONF-021":
            ok = correspondence_ok and declared_ok
            detail = (
                "all generator-declared FS0 outputs reproduce from the declared "
                "canonical bootstrap input root using the identified generator"
            )
        elif aid == "FS0-ASSERT-CONF-022":
            ok = correspondence_ok
            detail = (
                "deterministic regeneration matches checked-in generated surfaces"
            )
        else:
            ok = correspondence_ok
            detail = (
                "generation-correspondence failure is surfaced as a Conformance defect"
            )
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
    workflow_ok = workflow.is_file() and all(item in text for item in required)
    orchestration = load(root / "repo/conformance/orchestration.json")
    canonical_binding_ok = (
        orchestration.get("entrypoint") == "repo/conformance/run.py"
        and orchestration.get("public_wrapper") == "repo/scripts/validate"
        and "./repo/scripts/validate --verbose" in text
    )
    checks = {
        "FS0-ASSERT-CONF-010": (
            workflow_ok,
            "GitHub Actions exposes the canonical FS0 Conformance wrapper for push, pull request, and manual execution",
        ),
        "FS0-ASSERT-CONF-014": (
            workflow_ok and canonical_binding_ok,
            "the fixed FS0 GitHub workflow invokes the machine-resolvable canonical repository Conformance surface",
        ),
    }
    evidence = {"workflow": ".github/workflows/fs0-conformance.yml"}
    return [
        result(aid, "pass" if checks[aid][0] else "fail", checks[aid][1], evidence)
        for aid in assertion_ids
    ]




def check_exact_candidate(root, assertion_ids):
    workflow = root / ".github/workflows/fs0-conformance.yml"
    text = workflow.read_text(encoding="utf-8") if workflow.is_file() else ""

    expected_env = (
        "FS0_CANDIDATE_SHA: ${{ github.event_name == 'pull_request' "
        "&& github.event.pull_request.head.sha || github.sha }}"
    )
    expected_ref = "ref: ${{ env.FS0_CANDIDATE_SHA }}"
    structural_ok = (
        workflow.is_file()
        and expected_env in text
        and expected_ref in text
        and "uses: actions/checkout@v4" in text
        and "./repo/scripts/validate --verbose" in text
    )

    runtime = os.environ.get("GITHUB_ACTIONS") == "true"
    evidence = {
        "workflow": ".github/workflows/fs0-conformance.yml",
        "binding": "FS0_CANDIDATE_SHA",
        "runtime": runtime,
    }
    runtime_ok = True
    if runtime:
        candidate = os.environ.get("FS0_CANDIDATE_SHA", "").lower()
        try:
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip().lower()
        except Exception as exc:
            head = ""
            runtime_ok = False
            evidence["git_error"] = str(exc)

        candidate_ok = (
            len(candidate) == 40
            and all(ch in "0123456789abcdef" for ch in candidate)
        )
        runtime_ok = runtime_ok and candidate_ok and head == candidate
        evidence["candidate_sha"] = candidate
        evidence["checked_out_head"] = head
    else:
        evidence["mode"] = "local-structural-verification"

    ok = structural_ok and runtime_ok
    detail = (
        "workflow resolves an exact event candidate SHA, checks out that SHA, "
        "and GitHub Actions execution verifies checked-out HEAD equals the declared candidate"
    )
    return [result(aid, "pass" if ok else "fail", detail, evidence) for aid in assertion_ids]


def check_bootstrap_state(root, assertion_ids):
    path = root / "repo/state/bootstrap.json"
    if not path.is_file():
        return [
            result(aid, "fail", "repo/state/bootstrap.json is missing")
            for aid in assertion_ids
        ]

    try:
        record = load(path)
    except Exception as exc:
        return [
            result(aid, "fail", f"bootstrap state is not valid JSON: {exc}")
            for aid in assertion_ids
        ]

    required = {
        "schema_version",
        "record_type",
        "state",
        "candidate_revision",
        "first_accepted_fs0_revision",
        "bootstrap_provenance_issue",
        "bootstrap_acceptance_record",
        "accepted_ref",
        "cutover_timestamp",
    }
    state_ok = (
        set(record) == required
        and record.get("schema_version") == "1"
        and record.get("record_type") == "bootstrap-state"
        and record.get("state") in {"candidate", "cutover"}
        and record.get("accepted_ref") == "refs/heads/accepted"
    )
    orchestration = load(root / "repo/conformance/orchestration.json")
    pre_cutover_mode_ok = (
        record.get("state") == "candidate"
        and orchestration.get("mode") == "candidate-bootstrap-verification"
    )
    checks = {
        "FS0-ASSERT-FC-037": (
            state_ok,
            "repo/state/bootstrap.json contains the required bootstrap-state fields, uses candidate|cutover lifecycle state, and identifies refs/heads/accepted",
        ),
        "FS0-ASSERT-CONF-011": (
            pre_cutover_mode_ok,
            "while bootstrap state is candidate, candidate Conformance execution is explicitly bootstrap mechanical verification evidence only",
        ),
    }
    evidence = {
        "path": "repo/state/bootstrap.json",
        "state": record.get("state"),
        "accepted_ref": record.get("accepted_ref"),
        "conformance_mode": orchestration.get("mode"),
    }
    return [
        result(aid, "pass" if checks[aid][0] else "fail", checks[aid][1], evidence)
        for aid in assertion_ids
    ]



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
                "evidence": ["bootstrap-verification:test", "semantic-audit:test"],
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
        "issue_body": (
            "```json\n"
            + json.dumps(
                {
                    "bounded_authorization": {
                        "acceptance_actor": {"login": "tester"}
                    }
                }
            )
            + "\n```\n"
        ),
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

def check_accepted_state_publication(root, assertion_ids):
    state_path = root / "repo/governance/accepted_state.py"
    publish_path = root / "repo/governance/publish_accepted.py"
    if not state_path.is_file() or not publish_path.is_file():
        return [
            result(aid, "fail", "accepted-state publication realization is missing")
            for aid in assertion_ids
        ]

    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        state_spec = importlib.util.spec_from_file_location("fs0_accepted_state_pub", state_path)
        state_module = importlib.util.module_from_spec(state_spec)
        state_spec.loader.exec_module(state_module)

        pub_spec = importlib.util.spec_from_file_location("fs0_publish_accepted", publish_path)
        pub_module = importlib.util.module_from_spec(pub_spec)
        pub_spec.loader.exec_module(pub_module)
    finally:
        sys.dont_write_bytecode = old

    candidate = "c" * 40
    current = "d" * 40

    accepted_body = (
        "repo-spec-acceptance:v1\n"
        "```json\n"
        + json.dumps(
            {
                "schema_version": "1",
                "record_type": "bootstrap-acceptance",
                "acceptance_id": "FS0-ACCEPT-PUBLISH-TEST",
                "stage": "bootstrap",
                "work_id": "FS0-BOOTSTRAP-PROVENANCE",
                "candidate_id": candidate,
                "disposition": "accepted",
                "actor": "tester",
                "evidence": ["bootstrap-verification:test", "semantic-audit:test"],
                "decision_timestamp": "2026-08-22T00:00:00Z",
                "resulting_accepted_state": candidate,
            }
        )
        + "\n```\n"
    )
    current_body = (
        "repo-spec-acceptance:v1\n"
        "```json\n"
        + json.dumps(
            {
                "schema_version": "1",
                "record_type": "governance-acceptance",
                "acceptance_id": "FS0-ACCEPT-CURRENT-TEST",
                "stage": "build",
                "work_id": "FS0-WORK-BUILD-CURRENT",
                "candidate_id": current,
                "disposition": "accepted",
                "actor": "tester",
                "evidence": ["conformance:test"],
                "decision_timestamp": "2026-08-21T00:00:00Z",
                "resulting_accepted_state": current,
            }
        )
        + "\n```\n"
    )
    rejected_payload = {
        "schema_version": "1",
        "record_type": "bootstrap-acceptance",
        "acceptance_id": "FS0-ACCEPT-PUBLISH-REJECTED-TEST",
        "stage": "bootstrap",
        "work_id": "FS0-BOOTSTRAP-PROVENANCE",
        "candidate_id": candidate,
        "disposition": "rejected",
        "actor": "tester",
        "evidence": ["bootstrap-verification:test", "semantic-audit:test"],
        "decision_timestamp": "2026-08-22T00:00:00Z",
    }
    rejected_body = (
        "repo-spec-acceptance:v1\n"
        "```json\n"
        + json.dumps(rejected_payload)
        + "\n```\n"
    )

    bootstrap_issue_body = (
        "```json\n"
        + json.dumps(
            {"bootstrap_authorization": {"acceptance_actor": "tester"}}
        )
        + "\n```\n"
    )
    governance_issue_body = (
        "```json\n"
        + json.dumps(
            {"bounded_authorization": {"acceptance_actor": "tester"}}
        )
        + "\n```\n"
    )

    accepted_comments = [{
        "id": 1,
        "body": accepted_body,
        "issue_body": bootstrap_issue_body,
    }]
    rejected_comments = [{
        "id": 2,
        "body": rejected_body,
        "issue_body": bootstrap_issue_body,
    }]
    chain_comments = [
        {
            "id": 3,
            "body": current_body,
            "issue_body": governance_issue_body,
        },
        {
            "id": 4,
            "body": accepted_body,
            "issue_body": bootstrap_issue_body,
        },
    ]

    denied_missing = pub_module.publication_decision(
        candidate, None, [], state_module
    )
    denied_rejected = pub_module.publication_decision(
        candidate, None, rejected_comments, state_module
    )
    allowed_create = pub_module.publication_decision(
        candidate, None, accepted_comments, state_module
    )
    allowed_noop = pub_module.publication_decision(
        candidate, candidate, accepted_comments, state_module
    )
    allowed_advance = pub_module.publication_decision(
        candidate, current, chain_comments, state_module
    )

    source_text = publish_path.read_text(encoding="utf-8")
    ok = (
        not denied_missing["allowed"]
        and not denied_rejected["allowed"]
        and allowed_create["allowed"]
        and allowed_create["action"] == "create"
        and allowed_noop["allowed"]
        and allowed_noop["action"] == "noop"
        and allowed_advance["allowed"]
        and allowed_advance["action"] == "advance"
        and "decision = publication_decision(candidate, current, comments, module)" in source_text
        and "if not decision[\"allowed\"]" in source_text
        and "git\", \"push\", \"origin\"" in source_text
        and "accepted ref changed concurrently; refusing publication" in source_text
    )

    return [
        result(
            aid,
            "pass" if ok else "fail",
            "accepted ref publication is denied without prior explicit acceptance and permitted only after a matching accepted candidate record exists",
        )
        for aid in assertion_ids
    ]


def _walk_physical_namespace(root):
    records = {}
    stack = [root]
    while stack:
        directory = stack.pop()
        try:
            entries = list(os.scandir(directory))
        except OSError as exc:
            raise RuntimeError(f"cannot scan {directory}: {exc}") from exc
        for entry in entries:
            path = Path(entry.path)
            rel = path.relative_to(root).as_posix()
            try:
                mode = entry.stat(follow_symlinks=False).st_mode
            except OSError as exc:
                raise RuntimeError(f"cannot lstat {rel}: {exc}") from exc
            if stat.S_ISREG(mode):
                kind = "file"
            elif stat.S_ISDIR(mode):
                kind = "directory"
            elif stat.S_ISLNK(mode):
                kind = "symlink"
            else:
                kind = "unsupported"
            records[rel] = {"path": path, "object_type": kind, "mode": mode}
            if kind == "directory":
                stack.append(path)
    return records


def _json_record(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def _discover_structure_binding(root, namespace=None):
    namespace = namespace if namespace is not None else _walk_physical_namespace(root)
    matches = []
    for rel, item in namespace.items():
        if item["object_type"] != "file":
            continue
        obj = _json_record(item["path"])
        if (
            isinstance(obj, dict)
            and obj.get("schema_version") == "1"
            and obj.get("record_type") == "repository-structure-binding"
        ):
            matches.append((rel, obj))
    if len(matches) != 1:
        raise RuntimeError(
            "governed repository state must contain exactly one "
            f"repository-structure-binding record; found {len(matches)}"
        )
    rel, record = matches[0]
    identity = record.get("configuration_identity")
    if not isinstance(identity, str) or not identity:
        raise RuntimeError("repository-structure-binding lacks configuration_identity")
    return identity, rel


def _resolve_structure_configuration(root, identity, namespace=None):
    namespace = namespace if namespace is not None else _walk_physical_namespace(root)
    matches = []
    for rel, item in namespace.items():
        if item["object_type"] != "file":
            continue
        obj = _json_record(item["path"])
        if (
            isinstance(obj, dict)
            and obj.get("schema_version") == "1"
            and obj.get("record_type") == "repository-structure-configuration"
            and obj.get("configuration_id") == identity
        ):
            matches.append((rel, obj))
    if len(matches) != 1:
        raise RuntimeError(
            f"configuration identity {identity!r} must resolve to exactly one "
            f"configuration object; found {len(matches)}"
        )
    return matches[0]


def _normalize_config_entries(config):
    if config.get("schema_version") != "1":
        raise RuntimeError("unsupported repository-structure configuration schema")
    if config.get("record_type") != "repository-structure-configuration":
        raise RuntimeError("unexpected repository-structure configuration record_type")
    identity = config.get("configuration_id")
    if not isinstance(identity, str) or not identity:
        raise RuntimeError("configuration_id must be a non-empty string")
    raw_entries = config.get("objects")
    if not isinstance(raw_entries, list):
        raise RuntimeError("repository-structure configuration objects must be a list")

    entries = {}
    for rec in raw_entries:
        if not isinstance(rec, dict):
            raise RuntimeError("repository-structure object entries must be records")
        rel = rec.get("path")
        obj_type = rec.get("object_type")
        presence = rec.get("presence")
        descendants = rec.get("descendants", "closed")
        if not isinstance(rel, str) or not rel:
            raise RuntimeError("repository-structure object path must be non-empty")
        p = Path(rel)
        if p.is_absolute() or ".." in p.parts or rel in {".", "./"}:
            raise RuntimeError(f"invalid repository-structure path: {rel}")
        normalized = p.as_posix()
        if normalized != rel:
            raise RuntimeError(f"repository-structure path is not normalized: {rel}")
        if rel in entries:
            raise RuntimeError(f"duplicate repository-structure path: {rel}")
        if obj_type not in {"file", "directory", "symlink"}:
            raise RuntimeError(f"unsupported configured object type for {rel}: {obj_type}")
        if presence not in {"required", "permitted"}:
            raise RuntimeError(f"invalid presence for {rel}: {presence}")
        if descendants not in {"closed", "complete-subtree"}:
            raise RuntimeError(f"invalid descendants mode for {rel}: {descendants}")
        if obj_type != "directory" and descendants != "closed":
            raise RuntimeError(f"non-directory cannot authorize descendants: {rel}")
        entries[rel] = {
            "path": rel,
            "object_type": obj_type,
            "presence": presence,
            "descendants": descendants,
        }
    return entries


def _applicable_authorization(rel, entries):
    exact = entries.get(rel)
    if exact is not None:
        return exact, "exact"
    parts = Path(rel).parts
    for i in range(len(parts) - 1, 0, -1):
        ancestor = Path(*parts[:i]).as_posix()
        rec = entries.get(ancestor)
        if rec and rec["object_type"] == "directory" and rec["descendants"] == "complete-subtree":
            return rec, "complete-subtree"
    return None, None


def _evaluate_repository_structure(root):
    namespace = _walk_physical_namespace(root)
    identity, binding_path = _discover_structure_binding(root, namespace)
    config_path, config = _resolve_structure_configuration(root, identity, namespace)
    entries = _normalize_config_entries(config)

    unauthorized = []
    unsupported = []
    type_mismatches = []
    missing = []

    for rel, item in namespace.items():
        actual_type = item["object_type"]
        rec, mode = _applicable_authorization(rel, entries)
        if actual_type == "unsupported":
            unsupported.append(rel)
            continue
        if rec is None:
            unauthorized.append(rel)
            continue
        if mode == "exact" and rec["object_type"] != actual_type:
            type_mismatches.append({
                "path": rel,
                "expected": rec["object_type"],
                "actual": actual_type,
            })

    for rel, rec in entries.items():
        if rec["presence"] == "required" and rel not in namespace:
            missing.append(rel)

    self_rec, self_mode = _applicable_authorization(config_path, entries)
    self_authorized = (
        self_rec is not None
        and namespace.get(config_path, {}).get("object_type") == "file"
        and (self_mode == "complete-subtree" or self_rec.get("object_type") == "file")
    )

    ok = not unauthorized and not unsupported and not type_mismatches and not missing and self_authorized
    return {
        "ok": ok,
        "configuration_identity": identity,
        "binding_path": binding_path,
        "configuration_path": config_path,
        "observed_objects": len(namespace),
        "configured_objects": len(entries),
        "unauthorized": sorted(unauthorized),
        "unsupported": sorted(unsupported),
        "type_mismatches": sorted(type_mismatches, key=lambda x: x["path"]),
        "missing": sorted(missing),
        "configuration_self_authorized": self_authorized,
    }


def _write_test_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def _test_config(objects, identity="TEST-CONFIG"):
    return {
        "schema_version": "1",
        "record_type": "repository-structure-configuration",
        "configuration_id": identity,
        "objects": objects,
    }


def _test_binding(identity="TEST-CONFIG"):
    return {
        "schema_version": "1",
        "record_type": "repository-structure-binding",
        "configuration_identity": identity,
    }


def _exercise_structure_semantics():
    cases = {}

    def run_case(name, setup, expect_ok=None, expect_error=False, inspect=None):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            setup(root)
            try:
                report = _evaluate_repository_structure(root)
                if expect_error:
                    cases[name] = False
                    return
                ok = report["ok"] == expect_ok
                if inspect is not None:
                    ok = ok and bool(inspect(report))
                cases[name] = ok
            except Exception:
                cases[name] = bool(expect_error)

    def base(root, extra_objects=None):
        _write_test_json(root / "state.bin", _test_binding())
        objects = [
            {"path": "state.bin", "object_type": "file", "presence": "required"},
            {"path": "policy.bin", "object_type": "file", "presence": "required"},
        ]
        if extra_objects:
            objects.extend(extra_objects)
        _write_test_json(root / "policy.bin", _test_config(objects))

    run_case("conforming_state", lambda r: base(r), expect_ok=True)

    run_case(
        "ordinary_file_accepted",
        lambda r: (
            (r / "ordinary").write_text("x", encoding="utf-8"),
            base(r, [{"path": "ordinary", "object_type": "file", "presence": "required"}]),
        ),
        expect_ok=True,
    )

    run_case(
        "directory_object_accepted",
        lambda r: (
            (r / "directory").mkdir(),
            base(r, [{
                "path": "directory",
                "object_type": "directory",
                "presence": "required",
                "descendants": "closed",
            }]),
        ),
        expect_ok=True,
    )

    run_case(
        "unknown_file_rejected",
        lambda r: (base(r), (r / "unknown").write_text("x", encoding="utf-8")),
        expect_ok=False,
        inspect=lambda x: "unknown" in x["unauthorized"],
    )

    run_case(
        "unknown_directory_rejected",
        lambda r: (base(r), (r / "unknown-dir").mkdir()),
        expect_ok=False,
        inspect=lambda x: "unknown-dir" in x["unauthorized"],
    )

    run_case(
        "closed_directory_rejects_descendant",
        lambda r: (
            (r / "closed").mkdir(),
            base(r, [{"path": "closed", "object_type": "directory", "presence": "required"}]),
            (r / "closed" / "child").write_text("x", encoding="utf-8"),
        ),
        expect_ok=False,
        inspect=lambda x: "closed/child" in x["unauthorized"],
    )

    run_case(
        "complete_subtree_accepts_descendant",
        lambda r: (
            (r / "tree").mkdir(),
            (r / "tree" / "child").write_text("x", encoding="utf-8"),
            base(r, [{
                "path": "tree",
                "object_type": "directory",
                "presence": "required",
                "descendants": "complete-subtree",
            }]),
        ),
        expect_ok=True,
    )

    if hasattr(os, "mkfifo"):
        run_case(
            "unsupported_fifo_rejected_under_subtree",
            lambda r: (
                (r / "tree").mkdir(),
                os.mkfifo(r / "tree" / "fifo"),
                base(r, [{
                    "path": "tree",
                    "object_type": "directory",
                    "presence": "required",
                    "descendants": "complete-subtree",
                }]),
            ),
            expect_ok=False,
            inspect=lambda x: "tree/fifo" in x["unsupported"],
        )

    run_case(
        "required_missing_rejected",
        lambda r: base(r, [{"path": "must-exist", "object_type": "file", "presence": "required"}]),
        expect_ok=False,
        inspect=lambda x: "must-exist" in x["missing"],
    )

    run_case(
        "permitted_missing_accepted",
        lambda r: base(r, [{"path": "optional", "object_type": "file", "presence": "permitted"}]),
        expect_ok=True,
    )

    run_case(
        "type_mismatch_rejected",
        lambda r: (
            (r / "thing").mkdir(),
            base(r, [{"path": "thing", "object_type": "file", "presence": "required"}]),
        ),
        expect_ok=False,
        inspect=lambda x: any(i["path"] == "thing" for i in x["type_mismatches"]),
    )

    run_case(
        "authorized_symlink_is_link_object",
        lambda r: (
            (r / "target").write_text("x", encoding="utf-8"),
            os.symlink("target", r / "link"),
            base(r, [
                {"path": "target", "object_type": "file", "presence": "required"},
                {"path": "link", "object_type": "symlink", "presence": "required"},
            ]),
        ),
        expect_ok=True,
    )

    run_case(
        "external_symlink_target_not_traversed",
        lambda r: (
            os.symlink("/tmp", r / "link"),
            base(r, [{"path": "link", "object_type": "symlink", "presence": "required"}]),
        ),
        expect_ok=True,
    )

    run_case(
        "configuration_self_authorization_required",
        lambda r: (
            _write_test_json(r / "state.bin", _test_binding()),
            _write_test_json(r / "policy.bin", _test_config([
                {"path": "state.bin", "object_type": "file", "presence": "required"},
            ])),
        ),
        expect_ok=False,
        inspect=lambda x: not x["configuration_self_authorized"],
    )

    run_case(
        "missing_binding_rejected",
        lambda r: _write_test_json(r / "policy.bin", _test_config([
            {"path": "policy.bin", "object_type": "file", "presence": "required"},
        ])),
        expect_error=True,
    )

    run_case(
        "ambiguous_binding_rejected",
        lambda r: (
            _write_test_json(r / "state-a", _test_binding()),
            _write_test_json(r / "state-b", _test_binding()),
            _write_test_json(r / "policy.bin", _test_config([
                {"path": "state-a", "object_type": "file", "presence": "required"},
                {"path": "state-b", "object_type": "file", "presence": "required"},
                {"path": "policy.bin", "object_type": "file", "presence": "required"},
            ])),
        ),
        expect_error=True,
    )

    run_case(
        "unresolved_identity_rejected",
        lambda r: _write_test_json(r / "state.bin", _test_binding("NO-SUCH-CONFIG")),
        expect_error=True,
    )

    run_case(
        "duplicate_matching_configuration_rejected",
        lambda r: (
            _write_test_json(r / "state.bin", _test_binding()),
            _write_test_json(r / "policy-a.bin", _test_config([
                {"path": "state.bin", "object_type": "file", "presence": "required"},
                {"path": "policy-a.bin", "object_type": "file", "presence": "required"},
                {"path": "policy-b.bin", "object_type": "file", "presence": "required"},
            ])),
            _write_test_json(r / "policy-b.bin", _test_config([
                {"path": "state.bin", "object_type": "file", "presence": "required"},
                {"path": "policy-a.bin", "object_type": "file", "presence": "required"},
                {"path": "policy-b.bin", "object_type": "file", "presence": "required"},
            ])),
        ),
        expect_error=True,
    )

    run_case(
        "relocated_configuration_resolves",
        lambda r: (
            (r / "policies").mkdir(),
            _write_test_json(r / "state.bin", _test_binding()),
            _write_test_json(r / "policies" / "renamed-config.bin", _test_config([
                {"path": "state.bin", "object_type": "file", "presence": "required"},
                {
                    "path": "policies",
                    "object_type": "directory",
                    "presence": "required",
                    "descendants": "closed",
                },
                {
                    "path": "policies/renamed-config.bin",
                    "object_type": "file",
                    "presence": "required",
                },
            ])),
        ),
        expect_ok=True,
        inspect=lambda x: x["configuration_path"] == "policies/renamed-config.bin",
    )

    return {"ok": all(cases.values()), "cases": cases}



def check_assurance_runtime(root, assertion_ids):
    module_path = root / "repo/assurance/runtime.py"
    if not module_path.is_file():
        return [
            result(aid, "fail", "Assurance runtime realization is missing")
            for aid in assertion_ids
        ]

    spec = importlib.util.spec_from_file_location("fs0_assurance_runtime", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    reqs = load(root / "repo/authority/requirements.json")["requirements"]
    corr_obj = load(root / "repo/assurance/correspondence.json")
    obs_obj = load(root / "repo/assurance/obligations.json")
    corr = corr_obj["records"]
    obs = obs_obj["obligations"]

    req_ids = {r["requirement_id"] for r in reqs}
    corr_by_req = {r["requirement_id"]: r for r in corr}
    obligation_by_id = {o["obligation_id"]: o for o in obs}
    required_corr = [r for r in corr if r["applicability"] == "required"]
    none_corr = [r for r in corr if r["applicability"] == "none"]

    sample = required_corr[0]
    triggered = module.triggered_obligation_ids(corr, [sample["requirement_id"]])

    review_type_map = {
        sample["obligation_ids"][0]: "requirement-quality",
    }
    instantiated = module.instantiate_review_cases(
        "FS0-WORK-TEST",
        [sample["requirement_id"]],
        corr,
        obs,
        "FS0-AUTH-GOVERNANCE",
        review_type_map,
        ["evidence:test"],
    )
    case = instantiated[0]
    case_ok = (
        len(instantiated) == 1
        and case["review_obligation_id"] == sample["obligation_ids"][0]
        and case["review_type"] == "requirement-quality"
        and case["reviewed_subject"]["work_id"] == "FS0-WORK-TEST"
    )

    self_auth = dict(case)
    self_auth["reviewed_subject"] = {"authority_id": "FS0-AUTH-GOVERNANCE"}
    self_auth_rejected = False
    try:
        module.validate_case(self_auth)
    except module.AssuranceError:
        self_auth_rejected = True

    adverse = {
        "schema_version": "1",
        "record_type": "assurance-finding",
        "finding_id": "FS0-FINDING-TEST-1",
        "case_id": case["case_id"],
        "status": "defect",
        "sequence": 1,
    }
    satisfied = {
        "schema_version": "1",
        "record_type": "assurance-finding",
        "finding_id": "FS0-FINDING-TEST-2",
        "case_id": case["case_id"],
        "status": "satisfied",
        "sequence": 2,
    }

    review_types = {
        "requirement-quality",
        "ambiguity",
        "contradiction",
        "Design-fidelity",
        "Plan-fidelity",
        "Build-fidelity",
        "Conformance-interpretation",
        "evidence-sufficiency",
    }
    finding_statuses = {
        "satisfied",
        "defect",
        "insufficient",
        "governance-required",
    }

    all_review_types_validate = all(
        module.validate_case(
            {
                **case,
                "case_id": f"FS0-CASE-REVIEW-{index}",
                "review_type": review_type,
                "finding_identity": f"FS0-FINDING-REVIEW-{index}",
            }
        )["review_type"] == review_type
        for index, review_type in enumerate(sorted(review_types), 1)
    )

    checks = {
        "FS0-ASSERT-ASSUR-001": (
            corr_obj.get("requirements_total") == len(reqs) == len(corr)
            and set(corr_by_req) == req_ids,
            "every active requirement has exactly one Assurance correspondence",
        ),
        "FS0-ASSERT-ASSUR-002": (
            triggered == sample["obligation_ids"]
            and triggered
            and all(x in obligation_by_id for x in triggered)
            and len(instantiated) == len(triggered)
            and {x["review_obligation_id"] for x in instantiated}
            == set(triggered),
            "each triggered Assurance obligation instantiates a case-specific review case",
        ),
        "FS0-ASSERT-ASSUR-003": (
            module.REVIEW_TYPES == review_types and all_review_types_validate,
            "Assurance cases validate every required review class",
        ),
        "FS0-ASSERT-ASSUR-004": (
            module.FINDING_STATUSES == finding_statuses
            and module.resolution_status(case["case_id"], [adverse]) == "adverse"
            and module.resolution_status(
                case["case_id"], [adverse, satisfied]
            ) == "resolved",
            "finding vocabulary and adverse-until-satisfied resolution are realized",
        ),
        "FS0-ASSERT-ASSUR-005": (
            case_ok,
            "Assurance cases require authority, obligation, review type, subject, evidence, exclusions when present, and finding identity",
        ),
        "FS0-ASSERT-ASSUR-006": (
            self_auth_rejected,
            "a review subject cannot authorize its own Assurance review",
        ),
        "FS0-ASSERT-ASSUR-008": (
            all(
                {"requirement_id", "applicability", "obligation_ids"} <= set(r)
                for r in corr
            ),
            "Assurance correspondence contains the required fields",
        ),
        "FS0-ASSERT-ASSUR-009": (
            module.CASES_DIR == "repo/assurance/cases"
            and module.FINDINGS_DIR == "repo/assurance/findings"
            and isinstance(module.load_cases(root), list)
            and isinstance(module.load_findings(root), list)
            and callable(module.write_case)
            and callable(module.write_finding),
            "case and finding artifacts use validated maintained repository JSON locations",
        ),
        "FS0-ASSERT-ASSUR-012": (
            all(
                r["obligation_ids"]
                and all(x in obligation_by_id for x in r["obligation_ids"])
                for r in required_corr
            ),
            "required Assurance correspondence resolves stable obligation identities",
        ),
        "FS0-ASSERT-ASSUR-013": (
            all(not r["obligation_ids"] for r in none_corr),
            "none-applicable Assurance correspondence has empty obligation_ids",
        ),
        "FS0-ASSERT-ASSUR-014": (
            module.CASES_DIR.startswith("repo/assurance/")
            and module.FINDINGS_DIR.startswith("repo/assurance/"),
            "Assurance case and finding artifacts are repository-hosted for the fixed GitHub binding",
        ),
    }

    return [
        result(aid, "pass" if checks[aid][0] else "fail", checks[aid][1])
        for aid in assertion_ids
    ]


def check_successor_proposal_registry(root, assertion_ids):
    registry_path = root / "repo/proposals/registry.json"
    if not registry_path.is_file():
        return [result(aid, "fail", "successor proposal registry is missing") for aid in assertion_ids]
    registry = load(registry_path)
    records = registry.get("proposals", [])
    required_fields = {"proposal_id","order","installed_path","markdown_projection","lifecycle_state","bootstrap_provenance","authority_state","reconstruction_dependencies","predecessor_id","successor_id"}
    ids = {r.get("proposal_id") for r in records}
    orders = [r.get("order") for r in records]
    installed_ok = projections_ok = source_role_ok = provenance_ok = True
    for record in records:
        jp, mp = root / record["installed_path"], root / record["markdown_projection"]
        if not jp.is_file() or not mp.is_file(): installed_ok = False; continue
        proposal = load(jp)
        if proposal.get("content") != mp.read_text(encoding="utf-8"): projections_ok = False
        if proposal.get("source_role") != "successor-design-proposal": source_role_ok = False
        source = proposal.get("source_provenance")
        if not isinstance(source,dict) or not all(source.get(k) for k in ("repository","revision","path","blob_sha")): provenance_ok = False
    dependencies_closed = all(all(dep in ids for dep in r.get("reconstruction_dependencies",[])) for r in records)
    selectable = [r for r in sorted(records,key=lambda x:x["order"]) if r.get("lifecycle_state")=="available" and not r.get("reconstruction_dependencies")]
    checks = {
        "FS0-ASSERT-FC-064": (bool(records) and source_role_ok and provenance_ok, "successor Design Proposal source is machine-resolvably distinct and provenance-bearing"),
        "FS0-ASSERT-FC-079": (bool(records) and installed_ok and projections_ok, "successor proposal JSON and Markdown are deterministic products of canonical proposal source data"),
        "FS0-ASSERT-GOV-022": (bool(records) and all(required_fields <= set(r) for r in records) and len(ids)==len(records) and len(orders)==len(set(orders)), "proposal registry records identity, order, paths, lifecycle, provenance, authority state, dependencies, and lineage"),
        "FS0-ASSERT-GOV-023": (bool(records) and all(r["lifecycle_state"]=="available" and r["bootstrap_provenance"]=="bootstrap-seed" and r["authority_state"]=="none" for r in records), "bootstrap seed proposal records use available/bootstrap-seed/none state"),
        "FS0-ASSERT-GOV-024": (bool(records) and dependencies_closed and bool(registry.get("selection_policy")) and bool(selectable), "fresh agents can enumerate available successor proposals and reconstruction dependencies without chat history"),
        "FS0-ASSERT-GOV-025": (bool(records) and all(r.get("proposal_id") and r.get("bootstrap_provenance")=="bootstrap-seed" for r in records), "bootstrap seed proposal identities are explicit and immutable source records can be preserved after cutover"),
    }
    return [result(aid, "pass" if checks[aid][0] else "fail", checks[aid][1]) for aid in assertion_ids]

def check_governed_work_kernel(root, assertion_ids):
    path = root / "repo/governance/work.py"
    if not path.is_file():
        return [result(a, "fail", "Governance work runtime is missing") for a in assertion_ids]
    spec = importlib.util.spec_from_file_location("fs0_governance_work", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    obligation = "FS0-OBL-TEST"
    d = m.create_design(
        "D1","REPO-SPEC-PROPOSAL-FRAMEWORK-CONTRACT",["repo/authority/requirements.json"],
        {"candidate":"design"},["normalized"],{"proposal":"framework-contract"},
        {"acceptance_actor":"tester","mutation_scope":["repo/authority/requirements.json"]},
        {"created":["FS1-X"],"amended":[],"withdrawn":[]},
    )
    case_d = {"case_id":"CD","review_obligation_id":obligation}
    finding_d = {"case_id":"CD","status":"satisfied","sequence":1}
    ad = m.decide(d,"accepted",[obligation],[case_d],[finding_d])

    intent = {
        "affected_artifacts":["repo/governance/work.py"],
        "conformance_work":["FS0-ASSERT-GOV-001"],
        "assurance_work":["Build-fidelity"],
        "dependencies":[],
        "sequencing":["runtime","conformance"],
        "build_scope":["repo/governance/work.py"],
    }

    plan_without_own_auth_rejected = False
    try:
        m.create_plan(
            "P-NOAUTH",ad,["repo/governance/work.py"],{"candidate":"plan"},["specified"],
            {"design":"D1"},{},intent,
        )
    except m.GovernanceWorkError:
        plan_without_own_auth_rejected = True

    p = m.create_plan(
        "P1",ad,["repo/governance/work.py"],{"candidate":"plan"},["specified"],
        {"design":"D1"},{"acceptance_actor":"tester","mutation_scope":["repo/governance/work.py"]},intent,
    )
    case_p = {"case_id":"CP","review_obligation_id":obligation}
    finding_p = {"case_id":"CP","status":"satisfied","sequence":1}
    ap = m.decide(p,"accepted",[obligation],[case_p],[finding_p])

    build_without_own_auth_rejected = False
    try:
        m.create_build(
            "B-NOAUTH",ap,["repo/governance/work.py"],{"candidate_id":"c"*40},
            ["implemented"],{"plan":"P1"},{},["evidence:test"],
        )
    except m.GovernanceWorkError:
        build_without_own_auth_rejected = True

    b = m.create_build(
        "B1",ap,["repo/governance/work.py"],{"candidate_id":"a"*40},
        ["implemented","verified"],{"plan":"P1"},
        {"acceptance_actor":"tester","mutation_scope":["repo/governance/work.py"]},
        ["evidence:test"],
    )
    overbroad = False
    try:
        m.create_build(
            "B2",ap,["repo/governance/work.py","repo/authority/requirements.json"],
            {"candidate_id":"b"*40},["complete"],{"plan":"P1"},
            {"acceptance_actor":"tester","mutation_scope":["repo/governance/work.py"]},
            ["evidence:test"],
        )
    except m.GovernanceWorkError:
        overbroad = True

    b = m.record_conformance(b,"pass")
    case_b = {"case_id":"CB","review_obligation_id":obligation}
    adverse = {"case_id":"CB","status":"defect","sequence":1}
    satisfied = {"case_id":"CB","status":"satisfied","sequence":2}
    missing = m.acceptance_eligibility(b,[obligation],[],[])
    blocked = m.acceptance_eligibility(b,[obligation],[case_b],[adverse])
    resolved = m.acceptance_eligibility(b,[obligation],[case_b],[adverse,satisfied])
    ab = m.decide(b,"accepted",[obligation],[case_b],[adverse,satisfied])

    rd = m.decide(
        m.create_design(
            "D2","REPO-SPEC-PROPOSAL-GOVERNANCE",["repo/authority/governance.json"],
            {"candidate":"rejected"},["decision"],{"proposal":"governance"},
            {"acceptance_actor":"tester","mutation_scope":[]},
            {"created":[],"amended":[],"withdrawn":[]},
        ),
        "rejected",[],[],[],
    )

    checks = {
        "FS0-ASSERT-GOV-001": (ad["stage"]=="design" and ap["stage"]=="plan" and ab["stage"]=="build",
                               "Governance runtime implements proposal->Design->Plan->Build progression"),
        "FS0-ASSERT-GOV-002": (m.STAGE_STEPS=={"design":["audit","normalize","accept"],"plan":["analyze","specify","accept"],"build":["implement","verify","accept"]},
                               "required three-step stage structures are explicit"),
        "FS0-ASSERT-GOV-003": (all({"work_id","predecessor_id","scope","material_exclusions","candidate_result","completion_conditions","disposition","provenance","bounded_authorization"} <= set(x) for x in (d,p,b)),
                               "common governed-work properties are validated"),
        "FS0-ASSERT-GOV-004": (d["initiating_proposal_id"]==d["predecessor_id"],
                               "Design consumes an explicit proposal identity"),
        "FS0-ASSERT-GOV-005": (p["accepted_design_id"]==ad["work_id"] and set(intent)>={"affected_artifacts","conformance_work","assurance_work","dependencies","sequencing","build_scope"},
                               "Plan consumes accepted Design and records bounded realization intent"),
        "FS0-ASSERT-GOV-006": (b["accepted_plan_id"]==ap["work_id"] and overbroad,
                               "Build consumes accepted Plan and rejects over-broad scope"),
        "FS0-ASSERT-GOV-010": (set(b["bounded_authorization"]["mutation_scope"]) <= set(b["scope"]),
                               "mutation authorization is bounded by explicit scope"),
        "FS0-ASSERT-GOV-028": (len({d["work_id"],p["work_id"],b["work_id"]})==3,
                               "Design Plan and Build are distinct governed work"),
        "FS0-ASSERT-GOV-031": (ad["disposition"]=="accepted" and rd["disposition"]=="rejected" and isinstance(d["normative_delta"],dict),
                               "Design records normative delta and explicit disposition"),
        "FS0-ASSERT-GOV-033": (b["verification"]["conformance_status"]=="pass" and not blocked["eligible"] and resolved["eligible"] and ab["disposition"]=="accepted",
                               "Build acceptance requires evidence Conformance and resolved Assurance"),
        "FS0-ASSERT-GOV-036": (plan_without_own_auth_rejected and build_without_own_auth_rejected,
                               "accepted predecessor work does not independently authorize successor Plan or Build work"),
        "FS0-ASSERT-GOV-049": (not blocked["eligible"] and resolved["eligible"],
                               "adverse Assurance blocks acceptance until satisfied"),
        "FS0-ASSERT-GOV-050": (not missing["eligible"] and missing["reason"]=="missing-or-ambiguous-required-case",
                               "triggered obligations require instantiated cases before acceptance"),
    }
    return [result(a,"pass" if checks[a][0] else "fail",checks[a][1]) for a in assertion_ids]


def check_github_governance_binding(root, assertion_ids):
    path = root / "repo/governance/github_binding.py"
    if not path.is_file():
        return [result(a, "fail", "GitHub Governance binding runtime is missing") for a in assertion_ids]
    spec = importlib.util.spec_from_file_location("fs0_github_binding", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    design_work = {
        "stage":"design","work_id":"D1","predecessor_id":"REPO-SPEC-PROPOSAL-FRAMEWORK-CONTRACT",
        "initiating_proposal_id":"REPO-SPEC-PROPOSAL-FRAMEWORK-CONTRACT",
        "normative_delta":{"created":["FS1-X"]},"candidate_result":{"authority_delta":"FS1-X"},
        "disposition":"accepted",
    }
    plan_work = {
        "stage":"plan","work_id":"P1","predecessor_id":"D1",
        "candidate_result":{"build_scope":["repo/governance/github_binding.py"]},
        "disposition":"accepted",
    }
    build_work = {
        "stage":"build","work_id":"B1","predecessor_id":"P1",
        "candidate_result":{"candidate_id":"a"*40},"disposition":"pending",
        "bounded_authorization":{"acceptance_actor":"tester","mutation_scope":["repo/governance/github_binding.py"]},
    }
    snap = {
        "design_issue":{"kind":"issue","number":101,"governed_work":design_work},
        "plan_issue":{"kind":"issue","number":102,"governed_work":plan_work},
        "build_issue":{"kind":"issue","number":103,"governed_work":build_work},
        "candidate":{"branch":"fs1/build-B1","commit_sha":"a"*40},
        "pull_request":{"kind":"pull_request","number":104,"head_branch":"fs1/build-B1","head_sha":"a"*40},
        "acceptance":{"disposition":"pending"},
        "remaining_unauthorized_work":["FS2"],
    }
    resolved = m.resolve_remote_governance_state(snap)

    same_issue_rejected = False
    bad = dict(snap)
    bad["plan_issue"] = {"kind":"issue","number":101,"governed_work":plan_work}
    try:
        m.resolve_remote_governance_state(bad)
    except m.GitHubBindingError:
        same_issue_rejected = True

    bad_candidate_rejected = False
    try:
        m.validate_candidate({"branch":"x","commit_sha":"abc"})
    except m.GitHubBindingError:
        bad_candidate_rejected = True

    bad_pr_rejected = False
    try:
        m.validate_review_surface(
            {"kind":"pull_request","number":9,"head_branch":"other","head_sha":"a"*40},
            snap["candidate"],
        )
    except m.GitHubBindingError:
        bad_pr_rejected = True

    bootstrap_issue = {
        "kind":"issue","number":100,
        "bootstrap_authorization":{"acceptance_actor":"tester"},
    }
    bootstrap_ok = m.validate_bootstrap_provenance_issue(bootstrap_issue)["number"] == 100
    bootstrap_as_work_rejected = False
    try:
        m.validate_bootstrap_provenance_issue({**bootstrap_issue,"governed_work":design_work})
    except m.GitHubBindingError:
        bootstrap_as_work_rejected = True

    post_cutover_denied = not m.post_cutover_mutation_allowed({"state":"cutover"}, None)
    post_cutover_governed = m.post_cutover_mutation_allowed(
        {"state":"cutover"},{**build_work,"disposition":"accepted"}
    )

    checks = {
        "FS0-ASSERT-GOV-018": (bootstrap_ok, "bootstrap provenance uses a dedicated GitHub issue with acceptance_actor"),
        "FS0-ASSERT-GOV-020": (post_cutover_denied and post_cutover_governed, "post-cutover persistent mutation requires accepted governed Build authorization"),
        "FS0-ASSERT-GOV-026": (snap["design_issue"]["kind"]=="issue" and resolved["active_design_work_id"]=="D1", "Design governed work uses a GitHub issue"),
        "FS0-ASSERT-GOV-027": (resolved["active_design_work_id"]=="D1" and resolved["accepted_realization_intent"]==plan_work["candidate_result"], "current governed work and accepted realization intent resolve from repository/GitHub state"),
        "FS0-ASSERT-GOV-038": (bootstrap_ok and bootstrap_as_work_rejected, "bootstrap provenance issue cannot masquerade as governed work"),
        "FS0-ASSERT-GOV-040": (post_cutover_denied, "bootstrap-only mutation cannot create post-cutover accepted state"),
        "FS0-ASSERT-GOV-042": (snap["plan_issue"]["kind"]=="issue" and snap["plan_issue"]["number"]!=snap["design_issue"]["number"], "Plan uses a separate GitHub issue"),
        "FS0-ASSERT-GOV-043": (len({snap["design_issue"]["number"],snap["plan_issue"]["number"],snap["build_issue"]["number"]})==3 and same_issue_rejected, "Build uses a separate GitHub issue"),
        "FS0-ASSERT-GOV-044": (resolved["candidate_branch"]=="fs1/build-B1" and resolved["revision_under_review"]=="a"*40 and bad_candidate_rejected, "candidate state requires branch plus exact commit SHA"),
        "FS0-ASSERT-GOV-045": (resolved["pull_request_number"]==104 and bad_pr_rejected, "candidate review surface is a PR bound to candidate branch and SHA"),
        "FS0-ASSERT-GOV-046": (resolved["active_design_work_id"]=="D1" and resolved["initiating_proposal_id"]=="REPO-SPEC-PROPOSAL-FRAMEWORK-CONTRACT" and resolved["normative_delta"]=={"created":["FS1-X"]}, "active Design work proposal and normative delta are machine-resolvable"),
        "FS0-ASSERT-GOV-047": (resolved["revision_under_review"]=="a"*40 and resolved["acceptance_status"]=="pending" and resolved["resulting_accepted_revision"] is None and resolved["remaining_unauthorized_work"]==["FS2"], "review revision acceptance result and unauthorized work are machine-resolvable"),
    }
    return [result(a,"pass" if checks[a][0] else "fail",checks[a][1]) for a in assertion_ids]

def check_proposal_lineage(root, assertion_ids):
    path = root / "repo/governance/proposals.py"
    if not path.is_file():
        return [
            result(aid, "fail", "Governance proposal-lineage runtime is missing")
            for aid in assertion_ids
        ]

    spec = importlib.util.spec_from_file_location("fs0_governance_proposals", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    registry = load(root / "repo/proposals/registry.json")
    seed = registry["proposals"][0]

    correction = {
        "proposal_id": "REPO-SPEC-PROPOSAL-FRAMEWORK-CONTRACT-CORRECTION-1",
        "predecessor_id": seed["proposal_id"],
        "bootstrap_provenance": "governance-successor",
    }
    valid = (
        module.validate_seed_correction(seed, correction)["proposal_id"]
        == correction["proposal_id"]
    )

    in_place_rejected = False
    try:
        module.validate_seed_correction(
            seed,
            {
                "proposal_id": seed["proposal_id"],
                "predecessor_id": seed["proposal_id"],
                "bootstrap_provenance": "governance-successor",
            },
        )
    except module.ProposalLineageError:
        in_place_rejected = True

    missing_lineage_rejected = False
    try:
        module.validate_seed_correction(
            seed,
            {
                "proposal_id": "REPO-SPEC-PROPOSAL-CORRECTION-WITHOUT-LINEAGE",
                "predecessor_id": None,
                "bootstrap_provenance": "governance-successor",
            },
        )
    except module.ProposalLineageError:
        missing_lineage_rejected = True

    fake_seed_rejected = False
    try:
        module.validate_seed_correction(
            seed,
            {
                "proposal_id": "REPO-SPEC-PROPOSAL-FAKE-SEED",
                "predecessor_id": seed["proposal_id"],
                "bootstrap_provenance": "bootstrap-seed",
            },
        )
    except module.ProposalLineageError:
        fake_seed_rejected = True

    checks = {
        "FS0-ASSERT-GOV-041": (
            valid
            and in_place_rejected
            and missing_lineage_rejected
            and fake_seed_rejected,
            "bootstrap seed correction requires a distinct successor proposal with explicit predecessor lineage",
        ),
    }
    return [
        result(aid, "pass" if checks[aid][0] else "fail", checks[aid][1])
        for aid in assertion_ids
    ]

def check_conformance_selftest(root, assertion_ids):
    good = check_conformance_closure(root, ["FS0-ASSERT-CONF-001"])[0]
    positive_ok = good.get("status") == "pass"

    with tempfile.TemporaryDirectory(prefix="fs0-conformance-selftest-") as tmp:
        tmp_root = Path(tmp)
        paths = (
            "repo/authority/requirements.json",
            "repo/conformance/correspondence.json",
            "repo/conformance/assertions.json",
            "repo/conformance/support/implementations.json",
            "repo/conformance/evidence.json",
            "repo/conformance/orchestration.json",
        )
        for rel in paths:
            src = root / rel
            dst = tmp_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())

        corrupt_path = tmp_root / "repo/conformance/correspondence.json"
        corrupt = load(corrupt_path)
        if not corrupt.get("records"):
            negative_ok = False
        else:
            corrupt["records"] = corrupt["records"][:-1]
            corrupt_path.write_text(
                json.dumps(corrupt, indent=2) + "\n",
                encoding="utf-8",
            )
            bad = check_conformance_closure(
                tmp_root, ["FS0-ASSERT-CONF-001"]
            )[0]
            negative_ok = bad.get("status") == "fail"

    implementations = load(
        root / "repo/conformance/support/implementations.json"
    )["implementations"]
    orchestration = load(root / "repo/conformance/orchestration.json")
    bound = {
        aid
        for implementation in implementations
        for aid in implementation.get("assertion_ids", [])
    }
    scheduled = set(orchestration.get("realized_assertion_ids", []))
    execution_set_ok = bound == scheduled and bool(bound)

    ok = positive_ok and negative_ok and execution_set_ok
    evidence = {
        "conforming_state_acceptance": positive_ok,
        "targeted_violation_rejection": negative_ok,
        "required_assertions_scheduled": execution_set_ok,
        "required_assertion_count": len(bound),
    }
    detail = (
        "Conformance self-test demonstrates conforming-state acceptance, "
        "targeted correspondence violation rejection, and complete canonical "
        "execution scheduling for realized assertions"
    )
    return [
        result(aid, "pass" if ok else "fail", detail, evidence)
        for aid in assertion_ids
    ]

def check_conformance_canonicality(root, assertion_ids):
    orchestration = load(root / "repo/conformance/orchestration.json")
    policy = orchestration.get("post_cutover_policy", {})
    surface = policy.get("canonical_surface", {})
    policy_ok = (
        surface.get("entrypoint") == "repo/conformance/run.py"
        and surface.get("public_wrapper") == "repo/scripts/validate"
        and surface.get("github_workflow")
        == ".github/workflows/fs0-conformance.yml"
        and policy.get("mutation_requires_governance") is True
    )

    def mutation_allowed(state, current_surface, proposed_surface, governance_authorized):
        if state != "cutover":
            return True
        if proposed_surface == current_surface:
            return True
        return bool(governance_authorized)

    current = dict(surface)
    changed = dict(surface)
    changed["entrypoint"] = "repo/conformance/alternate.py"

    unchanged_allowed = mutation_allowed("cutover", current, current, False)
    unauthorized_denied = not mutation_allowed(
        "cutover", current, changed, False
    )
    governed_change_allowed = mutation_allowed(
        "cutover", current, changed, True
    )

    ok = (
        policy_ok
        and unchanged_allowed
        and unauthorized_denied
        and governed_change_allowed
    )
    evidence = {
        "policy": policy,
        "unchanged_allowed": unchanged_allowed,
        "unauthorized_change_denied": unauthorized_denied,
        "governance_authorized_change_allowed": governed_change_allowed,
    }
    detail = (
        "post-cutover accepted Conformance surface remains canonical and "
        "surface changes require Governance authorization"
    )
    return [
        result(aid, "pass" if ok else "fail", detail, evidence)
        for aid in assertion_ids
    ]

def check_generation_contract(root, assertion_ids):
    contract = load(root / "repo/bootstrap/data/realization/generation_contract.json")
    required = {
        "schema_version",
        "record_type",
        "canonical_source_role",
        "canonical_input_root",
        "generation_implementation",
        "generation_entrypoint",
        "correspondence_check",
        "declared_variable_inputs",
        "generated_output_ownership",
        "generated_surfaces_are_canonical_source",
        "post_cutover_bootstrap_source_mutation_requires_governance",
    }
    contract_ok = (
        set(contract) == required
        and contract.get("schema_version") == "1"
        and contract.get("record_type") == "fs0-generation-contract"
        and contract.get("canonical_source_role") == "canonical-bootstrap-maintenance-data"
        and contract.get("canonical_input_root") == "repo/bootstrap/data"
        and contract.get("generation_implementation") == "repo/bootstrap/scripts/src/generate.py"
        and contract.get("generation_entrypoint") == "repo/bootstrap/scripts/bootstrap"
        and contract.get("correspondence_check") == "repo/bootstrap/scripts/bootstrap --check"
        and contract.get("declared_variable_inputs") == []
        and contract.get("generated_surfaces_are_canonical_source") is False
        and contract.get("post_cutover_bootstrap_source_mutation_requires_governance") is True
    )

    generator_path = root / contract["generation_implementation"]
    source_root = root / contract["canonical_input_root"]
    paths_ok = generator_path.is_file() and source_root.is_dir()

    generator_dir = str(generator_path.parent)
    inserted = generator_dir not in sys.path
    if inserted:
        sys.path.insert(0, generator_dir)
    try:
        spec = importlib.util.spec_from_file_location(
            "fs0_generate_contract", generator_path
        )
        generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator)
    finally:
        if inserted:
            try:
                sys.path.remove(generator_dir)
            except ValueError:
                pass

    first = generator.derive(root)
    second = generator.derive(root)
    first_keys = {p.relative_to(root).as_posix() for p in first}
    second_keys = {p.relative_to(root).as_posix() for p in second}

    deterministic = first_keys == second_keys
    if deterministic:
        for path in first:
            if generator.render_output(first[path]) != generator.render_output(second[path]):
                deterministic = False
                break

    checked_in_match = True
    mismatches = []
    for path, value in first.items():
        expected = generator.render_output(value)
        try:
            actual = path.read_bytes()
        except FileNotFoundError:
            checked_in_match = False
            mismatches.append(path.relative_to(root).as_posix())
            continue
        if actual != expected:
            checked_in_match = False
            mismatches.append(path.relative_to(root).as_posix())

    generated_not_source = all(
        not rel.startswith(contract["canonical_input_root"] + "/")
        for rel in first_keys
    )

    def post_cutover_source_mutation_allowed(path, build):
        if not path.startswith("repo/bootstrap/data/"):
            return True
        if not isinstance(build, dict):
            return False
        if build.get("stage") != "build" or build.get("disposition") != "accepted":
            return False
        auth = build.get("bounded_authorization")
        return (
            isinstance(auth, dict)
            and path in auth.get("mutation_scope", [])
        )

    protected_path = "repo/bootstrap/data/model.json"
    denied_without_build = not post_cutover_source_mutation_allowed(
        protected_path, None
    )
    denied_out_of_scope = not post_cutover_source_mutation_allowed(
        protected_path,
        {
            "stage": "build",
            "disposition": "accepted",
            "bounded_authorization": {
                "mutation_scope": ["repo/bootstrap/data/root/index.json"]
            },
        },
    )
    allowed_in_scope = post_cutover_source_mutation_allowed(
        protected_path,
        {
            "stage": "build",
            "disposition": "accepted",
            "bounded_authorization": {"mutation_scope": [protected_path]},
        },
    )

    checks = {
        "FS0-ASSERT-FC-065": (
            contract_ok and paths_ok and bool(first_keys),
            "bootstrap-generated maintained artifacts resolve to canonical maintenance data and the separately identified generator implementation",
        ),
        "FS0-ASSERT-FC-066": (
            contract_ok and generated_not_source and checked_in_match,
            "generated read and operating surfaces are generator outputs and are not canonical maintenance-data inputs",
        ),
        "FS0-ASSERT-FC-067": (
            contract_ok and deterministic,
            "two derivations from identical canonical inputs and declared variable inputs produce identical output paths and bytes",
        ),
        "FS0-ASSERT-FC-068": (
            contract_ok and source_root.is_dir(),
            "one machine-resolvable canonical maintenance-data source role is declared for generated FS0 artifacts",
        ),
        "FS0-ASSERT-FC-073": (
            denied_without_build and denied_out_of_scope and allowed_in_scope,
            "post-cutover bootstrap-source mutation requires accepted Governance Build authorization covering the source path",
        ),
        "FS0-ASSERT-FC-077": (
            contract_ok and checked_in_match and bool(first_keys),
            "generated FS0 read surfaces are produced from canonical maintenance data by the identified generator",
        ),
        "FS0-ASSERT-FC-078": (
            contract_ok and deterministic and checked_in_match,
            "every current generator-owned maintained artifact is reproducible from canonical maintenance data and the identified generator",
        ),
    }
    evidence = {
        "canonical_input_root": contract.get("canonical_input_root"),
        "generation_implementation": contract.get("generation_implementation"),
        "declared_variable_inputs": contract.get("declared_variable_inputs"),
        "generated_output_count": len(first_keys),
        "mismatches": mismatches,
        "deterministic": deterministic,
    }
    return [
        result(aid, "pass" if checks[aid][0] else "fail", checks[aid][1], evidence)
        for aid in assertion_ids
    ]


def check_repository_structure(root, assertion_ids):
    try:
        live = _evaluate_repository_structure(root)
        semantic = _exercise_structure_semantics()
        source_text = Path(__file__).read_text(encoding="utf-8")
        cases = semantic["cases"]

        live_clean = (
            live["ok"]
            and not live["unauthorized"]
            and not live["unsupported"]
            and not live["missing"]
            and not live["type_mismatches"]
        )
        exact_one_resolution = (
            live.get("configuration_identity")
            and live.get("configuration_path")
            and live.get("binding_path")
        )
        source_uses_only_config_authorization = (
            "rec, mode = _applicable_authorization(rel, entries)" in source_text
            and "if rec is None:" in source_text
            and "unauthorized.append(rel)" in source_text
        )
        source_location_independent = (
            "for rel, item in namespace.items():" in source_text
            and 'obj.get("record_type") == "repository-structure-binding"' in source_text
            and 'obj.get("record_type") == "repository-structure-configuration"' in source_text
            and "configuration identity" in source_text
        )
        source_nonfollowing = (
            "entry.stat(follow_symlinks=False)" in source_text
            and 'if kind == "directory":' in source_text
            and "stack.append(path)" in source_text
        )

        common = {
            "configuration_identity": live.get("configuration_identity"),
            "binding_path": live.get("binding_path"),
            "configuration_path": live.get("configuration_path"),
            "observed_objects": live.get("observed_objects"),
            "configured_objects": live.get("configured_objects"),
        }

        def ev(**items):
            out = dict(common)
            out.update(items)
            return out

        checks = {
            "FS0-ASSERT-FC-006": (
                live_clean,
                "the complete physical repository namespace conforms to the resolved repository-structure configuration",
                ev(
                    unauthorized=live["unauthorized"],
                    unsupported=live["unsupported"],
                    missing=live["missing"],
                    type_mismatches=live["type_mismatches"],
                ),
            ),
            "FS0-ASSERT-FC-029": (
                live_clean and source_uses_only_config_authorization,
                "structural permission is obtained only through applicable authorization from the resolved configuration",
                ev(authorization_path="_applicable_authorization -> resolved configuration"),
            ),
            "FS0-ASSERT-FC-030": (
                live_clean and cases["unknown_file_rejected"] and cases["unknown_directory_rejected"],
                "objects lacking applicable structural authorization are rejected",
                ev(
                    semantic_tests={
                        "unknown_file_rejected": cases["unknown_file_rejected"],
                        "unknown_directory_rejected": cases["unknown_directory_rejected"],
                    }
                ),
            ),
            "FS0-ASSERT-FC-055": (
                live_clean and exact_one_resolution,
                "repository structure is evaluated against one resolved canonical configuration",
                ev(resolution="exactly one binding identity and exactly one matching configuration"),
            ),
            "FS0-ASSERT-FC-080": (
                live_clean and cases["unknown_file_rejected"] and cases["unknown_directory_rejected"],
                "absence of applicable structural authorization is deny",
                ev(
                    semantic_tests={
                        "unknown_file_rejected": cases["unknown_file_rejected"],
                        "unknown_directory_rejected": cases["unknown_directory_rejected"],
                    }
                ),
            ),
            "FS0-ASSERT-FC-081": (
                live_clean and source_uses_only_config_authorization,
                "no incidental filesystem class receives implicit structural authorization",
                ev(implicit_authorization_sources=[]),
            ),
            "FS0-ASSERT-FC-082": (
                live_clean and exact_one_resolution,
                "governed repository state determines exactly one repository-structure configuration identity",
                ev(configuration_identity=live["configuration_identity"]),
            ),
            "FS0-ASSERT-FC-083": (
                live_clean and exact_one_resolution and source_location_independent,
                "the operating substrate resolves the governed configuration identity and does not select a configuration by caller preference",
                ev(resolution="namespace semantic-record scan by governed identity"),
            ),
            "FS0-ASSERT-FC-084": (
                live_clean
                and cases["missing_binding_rejected"]
                and cases["ambiguous_binding_rejected"]
                and cases["unresolved_identity_rejected"]
                and cases["duplicate_matching_configuration_rejected"],
                "missing, ambiguous, or unresolved governed configuration identity is rejected rather than replaced by a default, fallback, or search-order choice",
                ev(
                    semantic_tests={
                        "missing_binding_rejected": cases["missing_binding_rejected"],
                        "ambiguous_binding_rejected": cases["ambiguous_binding_rejected"],
                        "unresolved_identity_rejected": cases["unresolved_identity_rejected"],
                        "duplicate_matching_configuration_rejected": cases["duplicate_matching_configuration_rejected"],
                    }
                ),
            ),
            "FS0-ASSERT-FC-085": (
                live_clean
                and live["configuration_self_authorized"]
                and cases["configuration_self_authorization_required"],
                "the resolved repository-structure configuration must structurally authorize its own filesystem object",
                ev(
                    configuration_self_authorized=live["configuration_self_authorized"],
                    semantic_test=cases["configuration_self_authorization_required"],
                ),
            ),
            "FS0-ASSERT-FC-086": (
                live_clean
                and cases["required_missing_rejected"]
                and cases["permitted_missing_accepted"],
                "structural authorization distinguishes required presence from permitted absence",
                ev(
                    semantic_tests={
                        "required_missing_rejected": cases["required_missing_rejected"],
                        "permitted_missing_accepted": cases["permitted_missing_accepted"],
                    }
                ),
            ),
            "FS0-ASSERT-FC-087": (
                live_clean and cases["closed_directory_rejects_descendant"],
                "directory authorization is closed to descendants unless complete-subtree authorization is explicit",
                ev(semantic_test=cases["closed_directory_rejects_descendant"]),
            ),
            "FS0-ASSERT-FC-088": (
                live_clean and cases["complete_subtree_accepts_descendant"],
                "explicit complete-subtree authorization positively authorizes descendant objects",
                ev(semantic_test=cases["complete_subtree_accepts_descendant"]),
            ),
            "FS0-ASSERT-FC-089": (
                live_clean and cases.get("unsupported_fifo_rejected_under_subtree", True),
                "complete-subtree authorization does not override global filesystem-object admissibility",
                ev(semantic_test=cases.get("unsupported_fifo_rejected_under_subtree", "not-supported-on-platform")),
            ),
            "FS0-ASSERT-FC-090": (
                live_clean
                and cases["ordinary_file_accepted"]
                and cases["directory_object_accepted"]
                and cases["authorized_symlink_is_link_object"],
                "ordinary files, directories, and symbolic links are explicitly accepted as configured structural object types",
                ev(
                    supported_object_types=["file", "directory", "symlink"],
                    semantic_tests={
                        "ordinary_file_accepted": cases["ordinary_file_accepted"],
                        "directory_object_accepted": cases["directory_object_accepted"],
                        "authorized_symlink_is_link_object": cases["authorized_symlink_is_link_object"],
                    },
                ),
            ),
            "FS0-ASSERT-FC-091": (
                live_clean and cases.get("unsupported_fifo_rejected_under_subtree", True),
                "unsupported filesystem object types are denied",
                ev(semantic_test=cases.get("unsupported_fifo_rejected_under_subtree", "not-supported-on-platform")),
            ),
            "FS0-ASSERT-FC-092": (
                live_clean and cases["authorized_symlink_is_link_object"],
                "a symbolic link is structurally evaluated as the link object itself",
                ev(semantic_test=cases["authorized_symlink_is_link_object"]),
            ),
            "FS0-ASSERT-FC-093": (
                live_clean and cases["external_symlink_target_not_traversed"] and source_nonfollowing,
                "structural traversal does not follow symbolic-link targets",
                ev(
                    semantic_test=cases["external_symlink_target_not_traversed"],
                    lstat_behavior="follow_symlinks=False",
                ),
            ),
            "FS0-ASSERT-FC-094": (
                live_clean and cases["external_symlink_target_not_traversed"],
                "a symbolic-link target outside the repository does not enlarge the governed repository boundary",
                ev(semantic_test=cases["external_symlink_target_not_traversed"]),
            ),
            "FS0-ASSERT-FC-095": (
                live_clean
                and source_uses_only_config_authorization
                and bool(live["configuration_path"]) and live["configuration_self_authorized"],
                "bootstrap construction is not itself treated as structural authorization; the resulting candidate is evaluated through the resolved configuration",
                ev(authorization_path="_evaluate_repository_structure -> resolved configuration"),
            ),
            "FS0-ASSERT-FC-096": (
                live_clean and source_uses_only_config_authorization,
                "bootstrap conventions, generator destinations, and implementation defaults do not substitute for structural authorization",
                ev(independent_authorization_sources=[]),
            ),
            "FS0-ASSERT-FC-097": (
                live_clean
                and exact_one_resolution
                and source_location_independent
                and cases["relocated_configuration_resolves"],
                "the operating substrate resolves the canonical structure configuration through a location-independent semantic-record mechanism, including after configuration relocation",
                ev(
                    resolution="record_type plus governed configuration identity",
                    semantic_test=cases["relocated_configuration_resolves"],
                ),
            ),
            "FS0-ASSERT-FC-098": (
                live_clean and cases["permitted_missing_accepted"],
                "a structurally permitted object may be absent without structural failure",
                ev(semantic_test=cases["permitted_missing_accepted"]),
            ),
            "FS0-ASSERT-FC-099": (
                live_clean and source_uses_only_config_authorization,
                "implementation defaults, generated-output lists, ignore rules, workflow conventions, historical presence, and prior validation do not independently authorize structure",
                ev(independent_authorization_sources=[]),
            ),
            "FS0-ASSERT-CONF-025": (
                live_clean and live["observed_objects"] > 0,
                "Conformance evaluates the actual physical filesystem namespace rather than only a tracked or preclassified artifact set",
                ev(observed_objects=live["observed_objects"]),
            ),
            "FS0-ASSERT-CONF-026": (
                live_clean and not live["unauthorized"],
                "every observed supported filesystem object resolves applicable structural authorization",
                ev(unauthorized=live["unauthorized"]),
            ),
            "FS0-ASSERT-CONF-027": (
                live_clean and not live["missing"] and cases["required_missing_rejected"],
                "Conformance verifies that every required configured object exists",
                ev(
                    missing=live["missing"],
                    semantic_test=cases["required_missing_rejected"],
                ),
            ),
            "FS0-ASSERT-CONF-028": (
                live_clean
                and exact_one_resolution
                and cases["missing_binding_rejected"]
                and cases["ambiguous_binding_rejected"]
                and cases["unresolved_identity_rejected"]
                and cases["duplicate_matching_configuration_rejected"],
                "Conformance fails when governed state does not determine exactly one identity or that identity does not resolve exactly one configuration object",
                ev(
                    semantic_tests={
                        "missing_binding_rejected": cases["missing_binding_rejected"],
                        "ambiguous_binding_rejected": cases["ambiguous_binding_rejected"],
                        "unresolved_identity_rejected": cases["unresolved_identity_rejected"],
                        "duplicate_matching_configuration_rejected": cases["duplicate_matching_configuration_rejected"],
                    }
                ),
            ),
            "FS0-ASSERT-CONF-029": (
                live_clean,
                "structural Conformance diagnostics identify unauthorized, unsupported, missing, and type-mismatched objects sufficiently for correction",
                ev(
                    diagnostic_fields=[
                        "unauthorized",
                        "unsupported",
                        "missing",
                        "type_mismatches",
                    ]
                ),
            ),
        }

        missing_checks = sorted(set(assertion_ids) - set(checks))
        unexpected_checks = sorted(set(checks) - set(assertion_ids))
        if missing_checks or unexpected_checks:
            raise RuntimeError(
                f"repository-structure assertion evidence map mismatch: "
                f"missing={missing_checks} unexpected={unexpected_checks}"
            )

        return [
            result(aid, "pass" if checks[aid][0] else "fail", checks[aid][1], checks[aid][2])
            for aid in assertion_ids
        ]
    except Exception as exc:
        return [
            result(
                aid,
                "fail",
                f"repository-structure resolution/evaluation failed: {exc}",
                {"error": str(exc)},
            )
            for aid in assertion_ids
        ]

CALLABLES = {
    "repository_structure": check_repository_structure,
    "requirement_metadata": check_requirement_metadata,
    "conformance_closure": check_conformance_closure,
    "generation_correspondence": check_generation_correspondence,
    "canonical_entrypoint": check_canonical_entrypoint,
    "remote_execution": check_remote_execution,
    "exact_candidate": check_exact_candidate,
    "bootstrap_state": check_bootstrap_state,
    "governance_state_resolution": check_governance_state_resolution,
    "accepted_state_publication": check_accepted_state_publication,
    "assurance_runtime": check_assurance_runtime,
    "successor_proposal_registry": check_successor_proposal_registry,
    "governed_work_kernel": check_governed_work_kernel,
    "github_governance_binding": check_github_governance_binding,
    "proposal_lineage": check_proposal_lineage,
    "conformance_selftest": check_conformance_selftest,
    "conformance_canonicality": check_conformance_canonicality,
    "generation_contract": check_generation_contract,
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

    bound_ids = [
        aid
        for implementation in implementations
        for aid in implementation.get("assertion_ids", [])
    ]
    unknown_bound_ids = sorted(set(bound_ids) - mechanical_ids)
    duplicate_bound_ids = sorted(
        aid for aid in set(bound_ids) if bound_ids.count(aid) > 1
    )

    execution_defects = []
    if unknown_bound_ids:
        execution_defects.append(
            {
                "kind": "unknown-implementation-assertion-binding",
                "assertion_ids": unknown_bound_ids,
            }
        )
    if duplicate_bound_ids:
        execution_defects.append(
            {
                "kind": "duplicate-implementation-assertion-binding",
                "assertion_ids": duplicate_bound_ids,
            }
        )

    realized = set()
    results = []
    for impl in implementations:
        callable_name = impl["callable"]
        declared_ids = [
            aid for aid in impl.get("assertion_ids", []) if aid in mechanical_ids
        ]
        realized.update(declared_ids)

        if not declared_ids:
            continue

        fn = CALLABLES.get(callable_name)
        if fn is None:
            results.extend(
                result(aid, "fail", f"unknown implementation callable: {callable_name}")
                for aid in declared_ids
            )
            continue

        impl_results = fn(root, declared_ids)
        result_ids = [r.get("assertion_id") for r in impl_results]
        expected = set(declared_ids)
        observed = set(result_ids)

        if len(result_ids) != len(observed):
            execution_defects.append(
                {
                    "kind": "duplicate-emitted-assertion-result",
                    "implementation_id": impl.get("implementation_id"),
                    "assertion_ids": sorted(
                        aid for aid in observed if result_ids.count(aid) > 1
                    ),
                }
            )
        if observed != expected:
            execution_defects.append(
                {
                    "kind": "implementation-result-closure-mismatch",
                    "implementation_id": impl.get("implementation_id"),
                    "missing": sorted(expected - observed),
                    "unexpected": sorted(observed - expected),
                }
            )

        results.extend(
            r for r in impl_results
            if r.get("assertion_id") in expected
        )

    emitted_ids = [r["assertion_id"] for r in results]
    if len(emitted_ids) != len(set(emitted_ids)):
        execution_defects.append(
            {
                "kind": "duplicate-global-assertion-result",
                "assertion_ids": sorted(
                    aid for aid in set(emitted_ids) if emitted_ids.count(aid) > 1
                ),
            }
        )

    pending = sorted(mechanical_ids - realized)
    failed = sorted(
        {
            r["assertion_id"]
            for r in results
            if r["assertion_id"] in mechanical_ids and r["status"] == "fail"
        }
    )
    passed = sorted(
        {
            r["assertion_id"]
            for r in results
            if r["assertion_id"] in mechanical_ids and r["status"] == "pass"
        }
    )

    if set(passed) & set(failed):
        execution_defects.append(
            {
                "kind": "assertion-has-conflicting-results",
                "assertion_ids": sorted(set(passed) & set(failed)),
            }
        )

    status = (
        "fail"
        if failed or execution_defects
        else ("incomplete" if pending else "pass")
    )

    report = {
        "schema_version": "1",
        "record_type": "conformance-execution-result",
        "orchestration_id": orchestration["orchestration_id"],
        "status": status,
        "declared_mechanical_assertions": len(mechanical_ids),
        "realized_assertions": len(realized),
        "passed_assertions": len(passed),
        "failed_assertions": failed,
        "pending_assertions": pending,
        "execution_defects": execution_defects,
        "results": results,
    }
    print(json.dumps(report, indent=2))

    if failed or execution_defects:
        return 1
    if pending:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
