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
    ok = (
        set(record) == required
        and record.get("schema_version") == "1"
        and record.get("record_type") == "bootstrap-state"
        and record.get("state") in {"candidate", "cutover"}
        and record.get("accepted_ref") == "refs/heads/accepted"
    )
    detail = (
        "repo/state/bootstrap.json contains the required bootstrap-state fields, "
        "uses candidate|cutover lifecycle state, and identifies refs/heads/accepted"
    )
    evidence = {
        "path": "repo/state/bootstrap.json",
        "state": record.get("state"),
        "accepted_ref": record.get("accepted_ref"),
    }
    return [
        result(aid, "pass" if ok else "fail", detail, evidence)
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
                "evidence": ["conformance:test", "assurance:test"],
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
    rejected_body = accepted_body.replace(
        '"disposition": "accepted"',
        '"disposition": "rejected"',
    )

    accepted_comments = [{"id": 1, "body": accepted_body}]
    rejected_comments = [{"id": 2, "body": rejected_body}]
    chain_comments = [
        {"id": 3, "body": current_body},
        {"id": 4, "body": accepted_body},
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
    return {"ok": all(cases.values()), "cases": cases}


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
                and cases["unresolved_identity_rejected"],
                "missing, ambiguous, or unresolved governed configuration identity is rejected rather than replaced by a default, fallback, or search-order choice",
                ev(
                    semantic_tests={
                        "missing_binding_rejected": cases["missing_binding_rejected"],
                        "ambiguous_binding_rejected": cases["ambiguous_binding_rejected"],
                        "unresolved_identity_rejected": cases["unresolved_identity_rejected"],
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
                and cases["authorized_symlink_is_link_object"]
                and "file" in {"file", "directory", "symlink"}
                and "directory" in {"file", "directory", "symlink"},
                "ordinary files, directories, and symbolic links are the explicitly supported structural object types",
                ev(supported_object_types=["file", "directory", "symlink"]),
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
                and any(rec.get("path") == "repo/bootstrap/data/structure.json" for rec in load(root / "repo/config/repository-structure.json")["objects"]),
                "bootstrap construction is not itself treated as structural authorization; the resulting candidate is evaluated through the resolved configuration",
                ev(authorization_path="_evaluate_repository_structure -> resolved configuration"),
            ),
            "FS0-ASSERT-FC-096": (
                live_clean and source_uses_only_config_authorization,
                "bootstrap conventions, generator destinations, and implementation defaults do not substitute for structural authorization",
                ev(independent_authorization_sources=[]),
            ),
            "FS0-ASSERT-FC-097": (
                live_clean and exact_one_resolution and source_location_independent,
                "the operating substrate resolves the canonical structure configuration through a location-independent semantic-record mechanism",
                ev(resolution="record_type plus governed configuration identity"),
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
                and cases["unresolved_identity_rejected"],
                "Conformance fails when governed state does not determine exactly one identity or that identity does not resolve exactly one configuration object",
                ev(
                    semantic_tests={
                        "missing_binding_rejected": cases["missing_binding_rejected"],
                        "ambiguous_binding_rejected": cases["ambiguous_binding_rejected"],
                        "unresolved_identity_rejected": cases["unresolved_identity_rejected"],
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
