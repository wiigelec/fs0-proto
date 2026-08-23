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


def derive_root_surfaces(root: Path):
    data_dir = root / "repo/bootstrap/data/root"
    index = load_json(data_dir / "index.json")
    if index.get("schema_version") != "1":
        raise SystemExit("unsupported generated root surface index schema")
    if index.get("record_type") != "generated-root-surface-index":
        raise SystemExit("unexpected generated root surface index record_type")

    records = index.get("artifacts")
    if not isinstance(records, list) or not records:
        raise SystemExit("generated root surface index must contain artifacts")

    outputs = {}
    seen_targets = set()
    for rec in records:
        source_rel = rec.get("source")
        target_rel = rec.get("target")
        if not isinstance(source_rel, str) or not source_rel:
            raise SystemExit("generated root surface source must be a non-empty path")
        if not isinstance(target_rel, str) or not target_rel:
            raise SystemExit("generated root surface target must be a non-empty path")

        source_path = Path(source_rel)
        target_path = Path(target_rel)
        if source_path.is_absolute() or ".." in source_path.parts:
            raise SystemExit(f"invalid generated root surface source: {source_rel}")
        if target_path.is_absolute() or ".." in target_path.parts:
            raise SystemExit(f"invalid generated root surface target: {target_rel}")
        if target_rel in seen_targets:
            raise SystemExit(f"duplicate generated root surface target: {target_rel}")

        source = data_dir / source_path
        if not source.is_file():
            raise SystemExit(f"missing generated root surface source: {source}")
        seen_targets.add(target_rel)
        outputs[root / target_path] = source.read_text(encoding="utf-8")

    return outputs




def derive_bootstrap_state(root: Path):
    source = root / "repo/bootstrap/data/state/bootstrap.json"
    record = load_json(source)

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
    if record.get("schema_version") != "1":
        raise SystemExit("unsupported bootstrap state schema")
    if record.get("record_type") != "bootstrap-state":
        raise SystemExit("unexpected bootstrap state record_type")
    if set(record) != required:
        missing = sorted(required - set(record))
        extra = sorted(set(record) - required)
        raise SystemExit(
            f"bootstrap state fields mismatch; missing={missing} extra={extra}"
        )
    if record.get("state") not in {"candidate", "cutover"}:
        raise SystemExit("bootstrap state must be candidate|cutover")
    if record.get("accepted_ref") != "refs/heads/accepted":
        raise SystemExit("bootstrap accepted_ref must be refs/heads/accepted")

    return {root / "repo/state/bootstrap.json": record}


def derive_repository_structure_state(root: Path):
    bootstrap_root = root / "repo/bootstrap"
    matches = []
    for path in bootstrap_root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if (
            isinstance(obj, dict)
            and obj.get("schema_version") == "1"
            and obj.get("record_type") == "repository-structure-configuration"
        ):
            matches.append((path, obj))

    if len(matches) != 1:
        raise SystemExit(
            "bootstrap payload must contain exactly one "
            f"repository-structure-configuration record; found {len(matches)}"
        )

    config_path, config = matches[0]

    required = {
        "schema_version",
        "record_type",
        "configuration_id",
        "objects",
    }
    if set(config) != required:
        missing = sorted(required - set(config))
        extra = sorted(set(config) - required)
        raise SystemExit(
            f"repository structure configuration fields mismatch; "
            f"missing={missing} extra={extra}"
        )

    identity = config.get("configuration_id")
    if not isinstance(identity, str) or not identity:
        raise SystemExit("repository structure configuration_id is invalid")

    objects = config.get("objects")
    if not isinstance(objects, list):
        raise SystemExit("repository structure configuration objects must be a list")

    seen = set()
    for rec in objects:
        if not isinstance(rec, dict):
            raise SystemExit("repository structure object entries must be records")
        rel = rec.get("path")
        obj_type = rec.get("object_type")
        presence = rec.get("presence")
        descendants = rec.get("descendants", "closed")

        if not isinstance(rel, str) or not rel:
            raise SystemExit("repository structure path must be non-empty")
        p = Path(rel)
        if p.is_absolute() or ".." in p.parts or rel in {".", "./"}:
            raise SystemExit(f"invalid repository structure path: {rel}")
        if p.as_posix() != rel:
            raise SystemExit(f"repository structure path is not normalized: {rel}")
        if rel in seen:
            raise SystemExit(f"duplicate repository structure path: {rel}")
        if obj_type not in {"file", "directory", "symlink"}:
            raise SystemExit(f"invalid repository structure object type: {rel}")
        if presence not in {"required", "permitted"}:
            raise SystemExit(f"invalid repository structure presence: {rel}")
        if descendants not in {"closed", "complete-subtree"}:
            raise SystemExit(f"invalid repository structure descendants mode: {rel}")
        if obj_type != "directory" and descendants != "closed":
            raise SystemExit(
                f"non-directory repository structure entry authorizes descendants: {rel}"
            )
        seen.add(rel)

    config_rel = config_path.relative_to(root).as_posix()
    required_binding = "repo/state/repository-structure-binding.json"
    for rel in (config_rel, required_binding):
        if rel not in seen:
            raise SystemExit(
                f"canonical repository structure configuration does not authorize "
                f"required object: {rel}"
            )

    binding = {
        "schema_version": "1",
        "record_type": "repository-structure-binding",
        "configuration_identity": identity,
    }
    return {
        root / "repo/state/repository-structure-binding.json": binding,
    }

def derive_governance_realization(root: Path):
    data_dir = root / "repo/bootstrap/data/realization"
    config = load_json(data_dir / "governance.json")
    if config.get("schema_version") != "1":
        raise SystemExit("unsupported Governance realization data schema")
    if config.get("record_type") != "governance-realization-data":
        raise SystemExit("unexpected Governance realization data record_type")

    artifacts = config.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise SystemExit("Governance realization must define artifacts")

    outputs = {}
    modes = {}
    seen_targets = set()
    for item in artifacts:
        source_rel = item.get("source")
        target_rel = item.get("target")
        mode = item.get("mode")
        if not isinstance(source_rel, str) or not source_rel:
            raise SystemExit("Governance realization source must be a non-empty path")
        if not isinstance(target_rel, str) or not target_rel:
            raise SystemExit("Governance realization target must be a non-empty path")
        source_path = Path(source_rel)
        target_path = Path(target_rel)
        if source_path.is_absolute() or ".." in source_path.parts:
            raise SystemExit(f"invalid Governance realization source: {source_rel}")
        if target_path.is_absolute() or ".." in target_path.parts:
            raise SystemExit(f"invalid Governance realization target: {target_rel}")
        if target_rel in seen_targets:
            raise SystemExit(f"duplicate Governance realization target: {target_rel}")
        if not isinstance(mode, str) or len(mode) != 4 or any(
            ch not in "01234567" for ch in mode
        ):
            raise SystemExit(f"invalid Governance realization mode for {target_rel}: {mode}")

        source = data_dir / source_path
        if not source.is_file():
            raise SystemExit(f"missing Governance realization source: {source}")
        seen_targets.add(target_rel)
        outputs[root / target_path] = source.read_text(encoding="utf-8")
        modes[target_rel] = mode

    return outputs, modes


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
    outputs.update(derive_bootstrap_state(root))
    outputs.update(derive_repository_structure_state(root))
    outputs.update(derive_conformance_realization(root, requirements, assertions))
    governance_outputs, _ = derive_governance_realization(root)
    outputs.update(governance_outputs)
    outputs.update(derive_root_surfaces(root))
    return outputs


def artifact_modes(root: Path):
    realization = load_json(
        root / "repo/bootstrap/data/realization/conformance.json"
    )
    modes = dict(realization.get("artifact_modes", {}))
    if not isinstance(modes, dict):
        raise SystemExit("artifact_modes must be an object")
    _, governance_modes = derive_governance_realization(root)
    modes.update(governance_modes)
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
