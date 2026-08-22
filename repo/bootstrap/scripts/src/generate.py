#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import stat
import sys
from pathlib import Path

from conformance_realization import derive_conformance_realization


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"missing bootstrap data: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON {path}: {exc}")


def canonical_bytes(obj) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def render_output(value) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    return canonical_bytes(value)


def repository_root() -> Path:
    cwd = Path.cwd().resolve()
    if not (cwd / ".git").exists():
        raise SystemExit("FS0 bootstrap must be invoked from repository root")
    if not (cwd / "repo/bootstrap/data/model.json").is_file():
        raise SystemExit("repo/bootstrap/data/model.json is missing")
    return cwd


def suffix(requirement_id: str, prefix: str) -> str:
    if not requirement_id.startswith(prefix):
        raise SystemExit(f"unexpected requirement identity: {requirement_id}")
    return requirement_id[len(prefix):]


def derived_id(requirement_id: str, requirement_prefix: str, derived_prefix: str) -> str:
    return f"{derived_prefix}{suffix(requirement_id, requirement_prefix)}"


def load_source(root: Path):
    data = root / "repo/bootstrap/data"
    model = load_json(data / "model.json")

    if model.get("schema_version") != "1":
        raise SystemExit("unsupported bootstrap model schema")
    if model.get("record_type") != "fs0-bootstrap-model":
        raise SystemExit("unexpected bootstrap model record_type")

    authority_order = model.get("authority_order")
    if not isinstance(authority_order, list) or not authority_order:
        raise SystemExit("bootstrap model authority_order must be a non-empty list")
    if len(authority_order) != len(set(authority_order)):
        raise SystemExit("bootstrap model authority_order contains duplicates")

    authorities = {}
    requirements = []
    requirements_by_authority = {}
    seen_requirements = set()

    req_defaults = model.get("requirement_defaults", {})
    authority_defaults = model.get("authority_defaults", {})
    constraints = model.get("requirement_constraints", {})

    max_chars = constraints.get("statement_max_chars")
    c_allowed = set(constraints.get("conformance_applicability", []))
    a_allowed = set(constraints.get("assurance_applicability", []))
    if not isinstance(max_chars, int) or max_chars < 1:
        raise SystemExit("bootstrap model statement_max_chars must be a positive integer")
    if not c_allowed or not a_allowed:
        raise SystemExit("bootstrap model applicability enumerations are missing")

    for authority_name in authority_order:
        authority_path = data / "authority" / f"{authority_name}.json"
        src = load_json(authority_path)
        aid = src.get("id")
        if not aid:
            raise SystemExit(f"{authority_path}: missing authority id")
        if aid in (a.get("id") for a in authorities.values()):
            raise SystemExit(f"duplicate authority id: {aid}")

        req_dir = data / "requirements" / authority_name
        if not req_dir.is_dir():
            raise SystemExit(f"missing requirement partition: {req_dir}")
        chunks = sorted(req_dir.glob("*.json"))
        if not chunks:
            raise SystemExit(f"empty requirement partition: {req_dir}")

        local = []
        for chunk_path in chunks:
            chunk = load_json(chunk_path)
            if chunk.get("authority") != aid:
                raise SystemExit(f"{chunk_path}: authority mismatch")
            records = chunk.get("requirements")
            if not isinstance(records, list) or not records:
                raise SystemExit(f"{chunk_path}: requirements must be a non-empty list")

            for item in records:
                rid = item.get("id")
                statement = item.get("statement")
                c = item.get("c")
                a = item.get("a")
                state = item.get("state", req_defaults.get("lifecycle_state"))

                if not rid or rid in seen_requirements:
                    raise SystemExit(f"invalid or duplicate requirement identity: {rid}")
                if not isinstance(statement, str) or not statement:
                    raise SystemExit(f"{rid}: missing requirement statement")
                if len(statement) > max_chars:
                    raise SystemExit(
                        f"{rid}: requirement statement exceeds {max_chars} characters"
                    )
                if c not in c_allowed:
                    raise SystemExit(f"{rid}: invalid Conformance applicability: {c}")
                if a not in a_allowed:
                    raise SystemExit(f"{rid}: invalid Assurance applicability: {a}")
                if not state:
                    raise SystemExit(f"{rid}: missing lifecycle state")

                expanded = {
                    "schema_version": "1",
                    "record_type": "requirement",
                    "requirement_id": rid,
                    "owner_authority_id": aid,
                    "statement": statement,
                    "lifecycle_state": state,
                    "conformance_applicability": c,
                    "assurance_applicability": a,
                }
                seen_requirements.add(rid)
                local.append(expanded)
                requirements.append(expanded)

        requirements_by_authority[authority_name] = local

        authority = {
            "schema_version": "1",
            "record_type": "authority",
            "authority_id": aid,
            "title": src["title"],
            "owner": src.get("owner", aid),
            "lifecycle_state": src.get(
                "lifecycle_state",
                authority_defaults.get("lifecycle_state"),
            ),
            "dependencies": src.get("dependencies", []),
            "delegates": src.get("delegates", []),
            "requirements": [r["requirement_id"] for r in local],
        }
        if "provenance" in src:
            authority["provenance"] = src["provenance"]
        authorities[authority_name] = authority

    return model, authority_order, authorities, requirements, requirements_by_authority


def derive_identity_surfaces(model, requirements):
    identity = model.get("identity", {})
    req_prefix = identity.get("requirement_prefix")
    assertion = identity.get("assertion", {})
    obligation = identity.get("obligation", {})

    assertion_prefix = assertion.get("prefix")
    obligation_prefix = obligation.get("prefix")
    if not req_prefix or not assertion_prefix or not obligation_prefix:
        raise SystemExit("bootstrap model identity prefixes are incomplete")

    conformance_records = []
    assertions = []
    assurance_records = []
    obligations = []

    for rec in requirements:
        rid = rec["requirement_id"]
        owner = rec["owner_authority_id"]
        c = rec["conformance_applicability"]
        a = rec["assurance_applicability"]

        aid = derived_id(rid, req_prefix, assertion_prefix)
        oid = derived_id(rid, req_prefix, obligation_prefix)

        conformance_records.append({
            "schema_version": "1",
            "record_type": "conformance-correspondence",
            "requirement_id": rid,
            "applicability": c,
            "assertion_ids": [aid] if c == "mechanical" else [],
        })
        if c == "mechanical":
            assertions.append({
                "schema_version": "1",
                "record_type": "assertion-definition",
                "assertion_id": aid,
                "requirement_id": rid,
                "role": "assertion",
                "derivation": {
                    "kind": assertion["derivation_kind"],
                    "requirement_id": rid,
                },
            })

        assurance_records.append({
            "schema_version": "1",
            "record_type": "assurance-correspondence",
            "requirement_id": rid,
            "applicability": a,
            "obligation_ids": [oid] if a == "required" else [],
        })
        if a == "required":
            objective = obligation["review_objective_template"].format(
                requirement_id=rid
            )
            obligations.append({
                "schema_version": "1",
                "record_type": "assurance-obligation-definition",
                "obligation_id": oid,
                "requirement_id": rid,
                "authorizing_authority_id": owner,
                "review_objective": objective,
                "derivation": {
                    "kind": obligation["derivation_kind"],
                    "requirement_id": rid,
                },
            })

    return conformance_records, assertions, assurance_records, obligations


def derive(root: Path):
    model, authority_order, authority, requirements, _ = load_source(root)
    c_records, assertions, a_records, obligations = derive_identity_surfaces(
        model, requirements
    )

    authority_ids = [authority[name]["authority_id"] for name in authority_order]
    total = len(requirements)

    outputs = {
        root / "repo/authority" / f"{name}.json": authority[name]
        for name in authority_order
    }
    outputs[root / "repo/authority/requirements.json"] = {
        "schema_version": "1",
        "record_type": "requirement-registry",
        "requirements_total": total,
        "authority_order": authority_ids,
        "requirements": requirements,
    }
    outputs[root / "repo/conformance/correspondence.json"] = {
        "schema_version": "1",
        "record_type": "conformance-correspondence-registry",
        "requirements_total": total,
        "records": c_records,
    }
    outputs[root / "repo/conformance/assertions.json"] = {
        "schema_version": "1",
        "record_type": "assertion-definition-registry",
        "derivation_policy": model["identity"]["assertion"]["derivation_policy"],
        "assertions": assertions,
    }
    outputs[root / "repo/assurance/correspondence.json"] = {
        "schema_version": "1",
        "record_type": "assurance-correspondence-registry",
        "requirements_total": total,
        "records": a_records,
    }
    outputs[root / "repo/assurance/obligations.json"] = {
        "schema_version": "1",
        "record_type": "assurance-obligation-registry",
        "derivation_policy": model["identity"]["obligation"]["derivation_policy"],
        "obligations": obligations,
    }
    outputs.update(derive_conformance_realization(root, requirements, assertions))
    return outputs


def artifact_modes(root: Path):
    realization = load_json(
        root / "repo/bootstrap/data/realization/conformance.json"
    )
    modes = realization.get("artifact_modes", {})
    if not isinstance(modes, dict):
        raise SystemExit("artifact_modes must be an object")
    return modes


def required_mode(root: Path, target: Path, modes) -> int:
    rel = str(target.relative_to(root))
    raw = modes.get(rel, "0644")
    if not isinstance(raw, str) or len(raw) != 4 or any(
        ch not in "01234567" for ch in raw
    ):
        raise SystemExit(f"invalid generated artifact mode for {rel}: {raw}")
    return int(raw, 8)


def main():
    parser = argparse.ArgumentParser(
        description="Generate FS0 normative, C/A identity, and Conformance realization surfaces"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify generated surfaces match bootstrap data without writing",
    )
    args = parser.parse_args()

    root = repository_root()
    outputs = derive(root)
    modes = artifact_modes(root)

    mismatches = []
    for target, obj in outputs.items():
        expected = render_output(obj)
        expected_mode = required_mode(root, target, modes)
        if args.check:
            try:
                actual = target.read_bytes()
                actual_mode = stat.S_IMODE(target.stat().st_mode)
            except FileNotFoundError:
                mismatches.append(str(target.relative_to(root)))
                continue
            if actual != expected or actual_mode != expected_mode:
                mismatches.append(str(target.relative_to(root)))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(expected)
            target.chmod(expected_mode)

    if args.check:
        if mismatches:
            print("FS0 generation correspondence: FAIL", file=sys.stderr)
            for item in mismatches:
                print(f"  mismatch: {item}", file=sys.stderr)
            raise SystemExit(1)
        print("FS0 generation correspondence: PASS")
    else:
        for target in outputs:
            print(target.relative_to(root))


if __name__ == "__main__":
    main()
