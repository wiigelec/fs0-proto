#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
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


def repository_root() -> Path:
    cwd = Path.cwd().resolve()
    if not (cwd / ".git").exists():
        raise SystemExit("FS0 bootstrap must be invoked from repository root")
    if not (cwd / "repo" / "bootstrap" / "data").is_dir():
        raise SystemExit("repo/bootstrap/data is missing")
    return cwd


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
        raise SystemExit("FS0.1 requires exactly 164 normalized requirements")
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
    return outputs


def main():
    parser = argparse.ArgumentParser(description="Generate FS0.1 normative read surfaces")
    parser.add_argument("--check", action="store_true", help="verify generated surfaces match bootstrap data without writing")
    args = parser.parse_args()

    root = repository_root()
    outputs = derive(root)

    mismatches = []
    for target, obj in outputs.items():
        expected = canonical_bytes(obj)
        if args.check:
            try:
                actual = target.read_bytes()
            except FileNotFoundError:
                mismatches.append(str(target.relative_to(root)))
                continue
            if actual != expected:
                mismatches.append(str(target.relative_to(root)))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(expected)

    if args.check:
        if mismatches:
            print("FS0.1 generation correspondence: FAIL", file=sys.stderr)
            for item in mismatches:
                print(f"  mismatch: {item}", file=sys.stderr)
            raise SystemExit(1)
        print("FS0.1 generation correspondence: PASS")
    else:
        for target in outputs:
            print(target.relative_to(root))


if __name__ == "__main__":
    main()
