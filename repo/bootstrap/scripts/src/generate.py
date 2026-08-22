#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import stat
import sys
from collections import Counter
from conformance_realization import derive_conformance_realization
from pathlib import Path

AUTH_NAMES = ("framework", "governance", "conformance", "assurance")
REQ_NAMES = ("framework", "governance", "conformance", "assurance")


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


def required_mode(root: Path, target: Path) -> int:
    rel = str(target.relative_to(root))
    data_path = root / "repo/bootstrap/data/conformance/realization.json"
    data = load_json(data_path)
    modes = data.get("artifact_modes", {})
    raw = modes.get(rel, "0644")
    if not isinstance(raw, str) or len(raw) != 4 or any(ch not in "01234567" for ch in raw):
        raise SystemExit(f"invalid generated artifact mode for {rel}: {raw}")
    return int(raw, 8)


def repository_root() -> Path:
    cwd = Path.cwd().resolve()
    if not (cwd / ".git").exists():
        raise SystemExit("FS0 bootstrap must be invoked from repository root")
    if not (cwd / "repo" / "bootstrap" / "data").is_dir():
        raise SystemExit("repo/bootstrap/data is missing")
    return cwd


def derived_suffix(requirement_id: str) -> str:
    if not requirement_id.startswith("FS0-"):
        raise SystemExit(f"unexpected requirement identity: {requirement_id}")
    return requirement_id[4:]


def assertion_id(requirement_id: str) -> str:
    return f"FS0-ASSERT-{derived_suffix(requirement_id)}"


def obligation_id(requirement_id: str) -> str:
    return f"FS0-OBL-{derived_suffix(requirement_id)}"


def derive(root: Path):
    data = root / "repo" / "bootstrap" / "data"
    authority_dir = data / "authority"
    requirements_dir = data / "requirements"

    authority = {name: load_json(authority_dir / f"{name}.json") for name in AUTH_NAMES}
    req_index = load_json(requirements_dir / "index.json")
    req_chunks = {name: load_json(requirements_dir / f"{name}.json") for name in REQ_NAMES}

    expected_order = [
        "FS0-AUTH-FRAMEWORK",
        "FS0-AUTH-GOVERNANCE",
        "FS0-AUTH-CONFORMANCE",
        "FS0-AUTH-ASSURANCE",
    ]
    if req_index.get("requirements_total") != 164:
        raise SystemExit("FS0.3 requires exactly 164 normalized requirements")
    if req_index.get("authority_order") != expected_order:
        raise SystemExit("unexpected requirement authority order")

    requirements = []
    seen = set()
    expected_owner = {
        "framework": "FS0-AUTH-FRAMEWORK",
        "governance": "FS0-AUTH-GOVERNANCE",
        "conformance": "FS0-AUTH-CONFORMANCE",
        "assurance": "FS0-AUTH-ASSURANCE",
    }

    for name in REQ_NAMES:
        chunk = req_chunks[name]
        if chunk.get("owner_authority_id") != expected_owner[name]:
            raise SystemExit(f"{name}: requirement chunk owner mismatch")
        for rec in chunk.get("requirements", []):
            rid = rec.get("requirement_id")
            if not rid or rid in seen:
                raise SystemExit(f"invalid or duplicate requirement identity: {rid}")
            if rec.get("owner_authority_id") != expected_owner[name]:
                raise SystemExit(f"{rid}: requirement owner mismatch")
            statement = rec.get("statement")
            if not isinstance(statement, str) or not statement:
                raise SystemExit(f"{rid}: missing requirement statement")
            if len(statement) > 300:
                raise SystemExit(f"{rid}: requirement statement exceeds 300 characters")
            if rec.get("conformance_applicability") not in {"mechanical", "none"}:
                raise SystemExit(f"{rid}: invalid Conformance applicability")
            if rec.get("assurance_applicability") not in {"required", "none"}:
                raise SystemExit(f"{rid}: invalid Assurance applicability")
            seen.add(rid)
            requirements.append(rec)

    if len(requirements) != 164:
        raise SystemExit(f"normalized requirement count is {len(requirements)}, expected 164")

    for name in AUTH_NAMES:
        doc = authority[name]
        ids = doc.get("requirements")
        if not isinstance(ids, list):
            raise SystemExit(f"{name}: authority document missing requirements list")
        chunk_ids = [rec["requirement_id"] for rec in req_chunks[name]["requirements"]]
        if ids != chunk_ids:
            raise SystemExit(f"{name}: authority requirement list does not match normalized requirement data")

    c_counts = Counter(r["conformance_applicability"] for r in requirements)
    a_counts = Counter(r["assurance_applicability"] for r in requirements)
    if c_counts != Counter({"mechanical": 139, "none": 25}):
        raise SystemExit(f"unexpected Conformance applicability counts: {dict(c_counts)}")
    if a_counts != Counter({"required": 100, "none": 64}):
        raise SystemExit(f"unexpected Assurance applicability counts: {dict(a_counts)}")

    conformance_records = []
    assertions = []
    assurance_records = []
    obligations = []

    for rec in requirements:
        rid = rec["requirement_id"]
        owner = rec["owner_authority_id"]
        c = rec["conformance_applicability"]
        a = rec["assurance_applicability"]

        aid = assertion_id(rid)
        oid = obligation_id(rid)

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
                    "kind": "canonical-requirement-coverage",
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
            obligations.append({
                "schema_version": "1",
                "record_type": "assurance-obligation-definition",
                "obligation_id": oid,
                "requirement_id": rid,
                "authorizing_authority_id": owner,
                "review_objective": (
                    f"Determine whether the governed review subject satisfies {rid} "
                    "semantically using applicable FS0 Assurance review capabilities."
                ),
                "derivation": {
                    "kind": "canonical-requirement-assurance",
                    "requirement_id": rid,
                },
            })

    if len(conformance_records) != 164 or len(assurance_records) != 164:
        raise SystemExit("C/A correspondence closure failure")
    if len(assertions) != 139:
        raise SystemExit(f"expected 139 assertion identities, found {len(assertions)}")
    if len(obligations) != 100:
        raise SystemExit(f"expected 100 Assurance obligation identities, found {len(obligations)}")
    if len({a["assertion_id"] for a in assertions}) != 139:
        raise SystemExit("duplicate assertion identity")
    if len({o["obligation_id"] for o in obligations}) != 100:
        raise SystemExit("duplicate Assurance obligation identity")

    outputs = {
        root / "repo" / "authority" / f"{name}.json": authority[name]
        for name in AUTH_NAMES
    }
    outputs[root / "repo" / "authority" / "requirements.json"] = {
        "schema_version": "1",
        "record_type": "requirement-registry",
        "requirements_total": 164,
        "authority_order": expected_order,
        "requirements": requirements,
    }
    outputs[root / "repo" / "conformance" / "correspondence.json"] = {
        "schema_version": "1",
        "record_type": "conformance-correspondence-registry",
        "requirements_total": 164,
        "records": conformance_records,
    }
    outputs[root / "repo" / "conformance" / "assertions.json"] = {
        "schema_version": "1",
        "record_type": "assertion-definition-registry",
        "derivation_policy": (
            "Exactly one initial stable assertion identity is derived for each requirement "
            "with conformance_applicability=mechanical. This registry defines assertion identity "
            "and requirement provenance only. Implementation, evidence, and gating bindings are "
            "separate realization layers and are not inferred by identity derivation."
        ),
        "assertions": assertions,
    }
    outputs[root / "repo" / "assurance" / "correspondence.json"] = {
        "schema_version": "1",
        "record_type": "assurance-correspondence-registry",
        "requirements_total": 164,
        "records": assurance_records,
    }
    outputs[root / "repo" / "assurance" / "obligations.json"] = {
        "schema_version": "1",
        "record_type": "assurance-obligation-registry",
        "derivation_policy": (
            "Exactly one initial stable review-obligation identity is derived for each requirement "
            "with assurance_applicability=required. Review cases instantiate obligations against "
            "governed subjects and evidence."
        ),
        "obligations": obligations,
    }
    outputs.update(derive_conformance_realization(root, requirements, assertions))
    return outputs


def main():
    parser = argparse.ArgumentParser(description="Generate FS0.3 normative, C/A identity, and Conformance realization surfaces")
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify generated surfaces match bootstrap data without writing",
    )
    args = parser.parse_args()

    root = repository_root()
    outputs = derive(root)

    mismatches = []
    for target, obj in outputs.items():
        expected = render_output(obj)
        expected_mode = required_mode(root, target)
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
            print("FS0.3 generation correspondence: FAIL", file=sys.stderr)
            for item in mismatches:
                print(f"  mismatch: {item}", file=sys.stderr)
            raise SystemExit(1)
        print("FS0.3 generation correspondence: PASS")
    else:
        for target in outputs:
            print(target.relative_to(root))


if __name__ == "__main__":
    main()
