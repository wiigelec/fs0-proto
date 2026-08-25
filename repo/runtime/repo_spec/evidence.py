"""Durable repository evidence and authority-state loading."""
from __future__ import annotations

import json
from pathlib import Path

from .errors import GovernanceError
from .jsonio import normalize_repo_path
from .normative import Authority, AuthorizationGraph, Delegation


def _inside(repository_root: Path, path: str | Path) -> Path:
    root = repository_root.resolve()
    p = Path(path)
    p = (root / p).resolve() if not p.is_absolute() else p.resolve()
    try:
        p.relative_to(root)
    except ValueError as exc:
        raise GovernanceError(
            "evidence-path-outside-repository",
            f"evidence path outside repository: {p}",
        ) from exc
    return p


def write_evidence(repository_root: Path, path: str | Path, value: dict) -> str:
    p = _inside(repository_root, path)
    p.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if p.exists():
        if p.read_text(encoding="utf-8") != encoded:
            raise GovernanceError(
                "evidence-conflict",
                f"refusing to replace different durable evidence: {p}",
            )
    else:
        tmp = p.with_name(p.name + ".tmp")
        tmp.write_text(encoded, encoding="utf-8")
        tmp.replace(p)
    return p.relative_to(repository_root.resolve()).as_posix()


def load_evidence(repository_root: Path, path: str | Path) -> dict:
    p = _inside(repository_root, path)
    if not p.is_file():
        raise GovernanceError("missing-evidence", f"missing evidence: {p}")
    value = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GovernanceError("invalid-evidence", f"evidence must be a JSON object: {p}")
    return value


def require_evidence_refs(repository_root: Path, refs) -> tuple[str, ...]:
    resolved = []
    for ref in refs:
        if not isinstance(ref, str) or not ref:
            raise GovernanceError(
                "invalid-evidence-reference",
                "evidence references must be non-empty repository paths",
            )
        rel = normalize_repo_path(ref)
        load_evidence(repository_root, rel)
        resolved.append(rel)
    if not resolved:
        raise GovernanceError(
            "missing-acceptance-evidence",
            "acceptance requires durable evidence references",
        )
    return tuple(resolved)


def load_authorization_graph(
    repository_root: Path,
    path: str | Path,
) -> AuthorizationGraph:
    value = load_evidence(repository_root, path)
    if value.get("schema_version") != "1" or value.get("artifact_type") != "authority-state":
        raise GovernanceError(
            "invalid-authority-state",
            "authority state requires schema_version 1 and artifact_type authority-state",
        )
    authorities = value.get("authorities")
    delegations = value.get("delegations")
    if (
        not isinstance(authorities, list)
        or not authorities
        or not all(isinstance(x, str) and x for x in authorities)
    ):
        raise GovernanceError(
            "invalid-authority-state",
            "authorities must be non-empty strings",
        )
    if not isinstance(delegations, list):
        raise GovernanceError("invalid-authority-state", "delegations must be an array")

    edges = []
    for delegation in delegations:
        if (
            not isinstance(delegation, dict)
            or set(delegation) != {"source", "target", "capability"}
        ):
            raise GovernanceError(
                "invalid-authority-state",
                "delegations require source, target, capability",
            )
        edges.append(
            Delegation(
                delegation["source"],
                delegation["target"],
                delegation["capability"],
            )
        )

    return AuthorizationGraph([Authority(x) for x in authorities], edges)
