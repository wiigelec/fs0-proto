#!/usr/bin/env python3
from __future__ import annotations
from copy import deepcopy

STAGE_STEPS = {
    "design": ["audit", "normalize", "accept"],
    "plan": ["analyze", "specify", "accept"],
    "build": ["implement", "verify", "accept"],
}
DISPOSITIONS = {"pending", "accepted", "rejected"}
ADVERSE_FINDINGS = {"defect", "insufficient", "governance-required"}

class GovernanceWorkError(ValueError):
    pass

def _nonempty(v):
    return isinstance(v, str) and bool(v.strip())
def _valid_actor(v):
    if not isinstance(v, dict):
        return False
    actor_id = v.get("id")
    return (
        not isinstance(actor_id, bool)
        and isinstance(actor_id, int)
        and actor_id > 0
        and ("login" not in v or _nonempty(v.get("login")))
    )

def _string_list(v, nonempty=False):
    return isinstance(v, list) and (bool(v) or not nonempty) and all(_nonempty(x) for x in v)

def validate_work(r):
    common = {
        "schema_version", "record_type", "stage", "stage_steps", "work_id",
        "predecessor_id", "scope", "material_exclusions", "candidate_result",
        "completion_conditions", "disposition", "provenance", "bounded_authorization",
    }
    if not isinstance(r, dict) or not common <= set(r):
        raise GovernanceWorkError("governed work lacks required fields")
    if r["schema_version"] != "1" or r["record_type"] != "governed-work":
        raise GovernanceWorkError("invalid governed-work envelope")
    stage = r.get("stage")
    if stage not in STAGE_STEPS or r.get("stage_steps") != STAGE_STEPS[stage]:
        raise GovernanceWorkError("invalid stage or stage_steps")
    if not _nonempty(r.get("work_id")) or not _nonempty(r.get("predecessor_id")):
        raise GovernanceWorkError("work_id and predecessor_id are required")
    if not _string_list(r.get("scope"), True):
        raise GovernanceWorkError("scope must be non-empty")
    if not _string_list(r.get("material_exclusions")):
        raise GovernanceWorkError("material_exclusions must be a string list")
    if not isinstance(r.get("candidate_result"), dict) or not r["candidate_result"]:
        raise GovernanceWorkError("candidate_result must be non-empty")
    if not _string_list(r.get("completion_conditions"), True):
        raise GovernanceWorkError("completion_conditions must be non-empty")
    if r.get("disposition") not in DISPOSITIONS:
        raise GovernanceWorkError("invalid disposition")
    if not isinstance(r.get("provenance"), dict) or not r["provenance"]:
        raise GovernanceWorkError("provenance must be non-empty")
    auth = r.get("bounded_authorization")
    if not isinstance(auth, dict) or not _valid_actor(auth.get("acceptance_actor")):
        raise GovernanceWorkError(
            "bounded_authorization.acceptance_actor requires positive GitHub user id"
        )
    if not _string_list(auth.get("mutation_scope", [])):
        raise GovernanceWorkError("mutation_scope must be a string list")
    if not set(auth.get("mutation_scope", [])) <= set(r["scope"]):
        raise GovernanceWorkError("mutation_scope exceeds work scope")

    if stage == "design":
        if not _nonempty(r.get("initiating_proposal_id")) or not isinstance(r.get("normative_delta"), dict):
            raise GovernanceWorkError("Design requires initiating proposal and normative_delta")
    elif stage == "plan":
        if not _nonempty(r.get("accepted_design_id")):
            raise GovernanceWorkError("Plan requires accepted_design_id")
        intent = r.get("realization_intent")
        fields = {"affected_artifacts", "conformance_work", "assurance_work", "dependencies", "sequencing", "build_scope"}
        if not isinstance(intent, dict) or not fields <= set(intent):
            raise GovernanceWorkError("Plan realization_intent incomplete")
        if any(not _string_list(intent.get(f)) for f in fields) or not intent["build_scope"]:
            raise GovernanceWorkError("Plan realization_intent fields invalid")
    else:
        if not _nonempty(r.get("accepted_plan_id")):
            raise GovernanceWorkError("Build requires accepted_plan_id")
        verification = r.get("verification")
        if not isinstance(verification, dict) or not _string_list(verification.get("evidence"), True):
            raise GovernanceWorkError("Build verification evidence required")
        if verification.get("conformance_status") not in {"pending", "pass", "fail"}:
            raise GovernanceWorkError("invalid Build conformance_status")
    return r

def create_design(work_id, proposal_id, scope, candidate_result, completion_conditions,
                  provenance, bounded_authorization, normative_delta, material_exclusions=None):
    return validate_work({
        "schema_version": "1", "record_type": "governed-work", "stage": "design",
        "stage_steps": STAGE_STEPS["design"], "work_id": work_id, "predecessor_id": proposal_id,
        "scope": list(scope), "material_exclusions": list(material_exclusions or []),
        "candidate_result": deepcopy(candidate_result), "completion_conditions": list(completion_conditions),
        "disposition": "pending", "provenance": deepcopy(provenance),
        "bounded_authorization": deepcopy(bounded_authorization),
        "initiating_proposal_id": proposal_id, "normative_delta": deepcopy(normative_delta),
    })

def create_plan(work_id, accepted_design, scope, candidate_result, completion_conditions,
                provenance, bounded_authorization, realization_intent, material_exclusions=None):
    d = validate_work(dict(accepted_design))
    if d["stage"] != "design" or d["disposition"] != "accepted":
        raise GovernanceWorkError("Plan requires accepted Design")
    return validate_work({
        "schema_version": "1", "record_type": "governed-work", "stage": "plan",
        "stage_steps": STAGE_STEPS["plan"], "work_id": work_id, "predecessor_id": d["work_id"],
        "scope": list(scope), "material_exclusions": list(material_exclusions or []),
        "candidate_result": deepcopy(candidate_result), "completion_conditions": list(completion_conditions),
        "disposition": "pending", "provenance": deepcopy(provenance),
        "bounded_authorization": deepcopy(bounded_authorization),
        "accepted_design_id": d["work_id"], "realization_intent": deepcopy(realization_intent),
    })

def create_build(work_id, accepted_plan, scope, candidate_result, completion_conditions,
                 provenance, bounded_authorization, evidence, material_exclusions=None):
    p = validate_work(dict(accepted_plan))
    if p["stage"] != "plan" or p["disposition"] != "accepted":
        raise GovernanceWorkError("Build requires accepted Plan")
    if not set(scope) <= set(p["realization_intent"]["build_scope"]):
        raise GovernanceWorkError("Build scope exceeds accepted Plan build_scope")
    return validate_work({
        "schema_version": "1", "record_type": "governed-work", "stage": "build",
        "stage_steps": STAGE_STEPS["build"], "work_id": work_id, "predecessor_id": p["work_id"],
        "scope": list(scope), "material_exclusions": list(material_exclusions or []),
        "candidate_result": deepcopy(candidate_result), "completion_conditions": list(completion_conditions),
        "disposition": "pending", "provenance": deepcopy(provenance),
        "bounded_authorization": deepcopy(bounded_authorization),
        "accepted_plan_id": p["work_id"],
        "verification": {"evidence": list(evidence), "conformance_status": "pending"},
    })

def record_conformance(work, status):
    r = deepcopy(validate_work(dict(work)))
    if r["stage"] != "build" or status not in {"pass", "fail"}:
        raise GovernanceWorkError("Build Conformance status must be pass|fail")
    r["verification"]["conformance_status"] = status
    return validate_work(r)

def _case_status(case_id, findings):
    relevant = [x for x in findings if isinstance(x, dict) and x.get("case_id") == case_id]
    if not relevant:
        return "missing"
    seqs = [x.get("sequence") for x in relevant]
    if any(not isinstance(x, int) or x < 1 for x in seqs) or len(seqs) != len(set(seqs)):
        raise GovernanceWorkError("invalid finding sequence")
    latest = max(relevant, key=lambda x: x["sequence"])
    if latest.get("status") == "satisfied":
        return "resolved"
    if latest.get("status") in ADVERSE_FINDINGS:
        return "adverse"
    raise GovernanceWorkError("invalid finding status")

def assurance_gate(triggered_obligation_ids, cases, findings):
    grouped = {}
    for case in cases:
        if not isinstance(case, dict) or not _nonempty(case.get("review_obligation_id")) or not _nonempty(case.get("case_id")):
            raise GovernanceWorkError("invalid Assurance case")
        grouped.setdefault(case["review_obligation_id"], []).append(case)
    missing = [oid for oid in triggered_obligation_ids if len(grouped.get(oid, [])) != 1]
    if missing:
        return {"eligible": False, "reason": "missing-or-ambiguous-required-case", "obligation_ids": missing}
    adverse = []
    for oid in triggered_obligation_ids:
        if _case_status(grouped[oid][0]["case_id"], findings) != "resolved":
            adverse.append(oid)
    if adverse:
        return {"eligible": False, "reason": "unresolved-adverse-assurance", "obligation_ids": adverse}
    return {"eligible": True, "reason": "satisfied", "obligation_ids": []}

def acceptance_eligibility(work, triggered_obligation_ids, cases, findings):
    r = validate_work(dict(work))
    gate = assurance_gate(triggered_obligation_ids, cases, findings)
    if not gate["eligible"]:
        return gate
    if r["stage"] == "build" and r["verification"]["conformance_status"] != "pass":
        return {"eligible": False, "reason": "conformance-not-passing", "obligation_ids": []}
    return {"eligible": True, "reason": "satisfied", "obligation_ids": []}

def decide(work, disposition, triggered_obligation_ids, cases, findings):
    if disposition not in {"accepted", "rejected"}:
        raise GovernanceWorkError("decision must be accepted|rejected")
    r = deepcopy(validate_work(dict(work)))
    if r["disposition"] != "pending":
        raise GovernanceWorkError("work already decided")
    if disposition == "accepted":
        gate = acceptance_eligibility(r, triggered_obligation_ids, cases, findings)
        if not gate["eligible"]:
            raise GovernanceWorkError("acceptance blocked: " + gate["reason"])
    r["disposition"] = disposition
    return validate_work(r)

def merge_accept(work, merge_actor, triggered_obligation_ids, cases, findings):
    r = deepcopy(validate_work(dict(work)))
    if r["disposition"] != "pending":
        raise GovernanceWorkError("work already decided")
    gate = acceptance_eligibility(r, triggered_obligation_ids, cases, findings)
    if not gate["eligible"]:
        raise GovernanceWorkError("merge acceptance blocked: " + gate["reason"])
    expected = r["bounded_authorization"]["acceptance_actor"]
    if not _valid_actor(merge_actor) or merge_actor.get("id") != expected.get("id"):
        raise GovernanceWorkError("merge actor is not authorized acceptance_actor")
    r["disposition"] = "accepted"
    r["provenance"] = deepcopy(r["provenance"])
    r["provenance"]["acceptance"] = {"kind":"pull-request-merge","actor":deepcopy(merge_actor)}
    return validate_work(r)
