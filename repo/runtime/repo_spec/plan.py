"""Closed modular Plan loading and predecessor-based executability checks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import PlanningError
from .functional_set import FunctionalSet, load_functional_set
from .jsonio import load_json, normalize_repo_path
from .normative import NormativeRequirement, parse_requirements
from .repository import Repository


@dataclass(frozen=True)
class FileChange:
    path: str
    operation: str
    purpose: str
    requirement_ids: tuple[str, ...]
    implementation: tuple[str, ...]
    validation_ids: tuple[str, ...]
    depends_on_paths: tuple[str, ...]


@dataclass(frozen=True)
class LogicalPlan:
    id: str
    title: str
    description: str
    root_path: str
    implementation_predecessor: str
    functional_set: FunctionalSet
    requirements: tuple[NormativeRequirement, ...]
    file_changes: tuple[FileChange, ...]
    execution: dict[str, Any]
    invariants: dict[str, Any]
    validation: dict[str, Any]
    completion: dict[str, Any]

    def requirement_map(self) -> dict[str, NormativeRequirement]:
        return {r.id: r for r in self.requirements}


def _plan_relative(value: str) -> str:
    value = normalize_repo_path(value)
    if value.startswith("repo/"):
        raise PlanningError("invalid-plan-document-path", f"Plan document reference must be relative to Plan directory: {value}")
    return value


def _common_document(doc: object, *, artifact_type: str, plan_id: str, path: Path) -> dict:
    if not isinstance(doc, dict):
        raise PlanningError("invalid-plan-document", f"{path} must contain an object")
    if doc.get("schema_version") != "1":
        raise PlanningError("invalid-plan-document-version", f"{path} schema_version must be 1")
    if doc.get("artifact_type") != artifact_type:
        raise PlanningError("invalid-plan-document-type", f"{path} artifact_type must be {artifact_type}")
    if doc.get("plan_id") != plan_id:
        raise PlanningError("plan-id-mismatch", f"{path} plan_id does not match {plan_id}")
    return doc


def _exists_at(repository: Repository, revision: str, path: str) -> bool:
    proc = repository._git("cat-file", "-e", f"{revision}:{path}", check=False)
    return proc.returncode == 0


def _parse_file_change(doc: dict, *, plan_id: str, path: Path) -> FileChange:
    doc = _common_document(doc, artifact_type="plan-file", plan_id=plan_id, path=path)
    fc = doc.get("file_change")
    if not isinstance(fc, dict):
        raise PlanningError("invalid-file-change", f"{path} file_change must be an object")
    target = normalize_repo_path(fc.get("path", ""))
    operation = fc.get("operation")
    if operation not in {"create", "modify", "delete", "regenerate"}:
        raise PlanningError("invalid-file-operation", f"{path} has invalid operation {operation!r}")
    purpose = fc.get("purpose")
    implementation = fc.get("implementation")
    req_ids = fc.get("requirement_ids")
    val_ids = fc.get("validation_ids")
    deps = fc.get("depends_on_paths")
    if not isinstance(purpose, str) or not purpose.strip():
        raise PlanningError("missing-file-purpose", f"{path} requires purpose")
    if not isinstance(implementation, list) or not implementation or any(not isinstance(x, str) or not x.strip() for x in implementation):
        raise PlanningError("invalid-implementation-intent", f"{path} requires non-empty implementation intent")
    if not isinstance(req_ids, list) or not req_ids or len(req_ids) != len(set(req_ids)):
        raise PlanningError("invalid-file-requirements", f"{path} requirement_ids must be unique and non-empty")
    if not isinstance(val_ids, list) or not val_ids or len(val_ids) != len(set(val_ids)):
        raise PlanningError("invalid-file-validations", f"{path} validation_ids must be unique and non-empty")
    if not isinstance(deps, list) or len(deps) != len(set(deps)):
        raise PlanningError("invalid-file-dependencies", f"{path} depends_on_paths must be a unique array")
    dep_paths = tuple(normalize_repo_path(x) for x in deps)
    return FileChange(
        target, operation, purpose, tuple(req_ids), tuple(implementation), tuple(val_ids), dep_paths
    )


def load_plan(plan_path: str | Path, repository: Repository) -> LogicalPlan:
    plan_path = Path(plan_path)
    base = plan_path.parent.resolve()
    root = load_json(plan_path)
    if not isinstance(root, dict):
        raise PlanningError("invalid-plan", "plan.json root must be an object")
    if root.get("schema_version") != "2" or root.get("artifact_type") != "plan":
        raise PlanningError("invalid-plan-header", "plan.json requires schema_version 2 and artifact_type plan")

    pmeta = root.get("plan")
    fsref = root.get("functional_set")
    pred = root.get("implementation_predecessor")
    docs = root.get("documents")
    if not all(isinstance(x, dict) for x in (pmeta, fsref, pred, docs)):
        raise PlanningError("invalid-plan-structure", "plan metadata, functional_set, predecessor, and documents must be objects")

    plan_id = pmeta.get("id")
    if not isinstance(plan_id, str) or not plan_id:
        raise PlanningError("invalid-plan-id", "Plan id must be non-empty")
    predecessor = pred.get("repository_revision")
    repository.require_revision(predecessor)

    fs_path = normalize_repo_path(fsref.get("path", ""))
    functional_set = load_functional_set(repository.root / fs_path, repository)
    if functional_set.id != fsref.get("id"):
        raise PlanningError("functional-set-id-mismatch", "Plan functional-set identity does not match referenced artifact")
    if predecessor != functional_set.accepted_predecessor:
        raise PlanningError("predecessor-mismatch", "Plan implementation predecessor must match functional-set accepted predecessor")

    required_doc_keys = {"requirements", "file_plans", "execution", "invariants", "validation", "completion"}
    if set(docs) != required_doc_keys:
        raise PlanningError("invalid-plan-documents", f"documents must contain exactly {sorted(required_doc_keys)}")

    refs = [
        docs["requirements"], docs["execution"], docs["invariants"], docs["validation"], docs["completion"],
        *docs["file_plans"],
    ]
    if any(not isinstance(x, str) for x in refs):
        raise PlanningError("invalid-plan-reference", "Plan document references must be strings")
    rel_refs = tuple(_plan_relative(x) for x in refs)
    if len(rel_refs) != len(set(rel_refs)):
        raise PlanningError("duplicate-plan-reference", "Plan document references must be unique")

    resolved: dict[str, dict] = {}
    for rel in rel_refs:
        path = (base / rel).resolve()
        try:
            path.relative_to(base)
        except ValueError as exc:
            raise PlanningError("plan-reference-escape", f"Plan reference escapes Plan directory: {rel}") from exc
        if not path.is_file():
            raise PlanningError("missing-plan-document", f"missing Plan document: {rel}")
        resolved[rel] = load_json(path)

    actual = {
        p.relative_to(base).as_posix()
        for p in base.rglob("*.json")
        if p.name not in {"functional-set.json", "plan.json"}
    }
    declared = set(rel_refs)
    if actual != declared:
        extra = sorted(actual - declared)
        missing = sorted(declared - actual)
        raise PlanningError("plan-graph-not-closed", f"Plan graph mismatch extra={extra} missing={missing}")

    req_rel = _plan_relative(docs["requirements"])
    reqdoc = _common_document(resolved[req_rel], artifact_type="plan-requirements", plan_id=plan_id, path=base / req_rel)
    requirements = parse_requirements(reqdoc.get("requirements"))
    req_ids = {r.id for r in requirements}

    file_changes: list[FileChange] = []
    for rel in docs["file_plans"]:
        rel = _plan_relative(rel)
        fc = _parse_file_change(resolved[rel], plan_id=plan_id, path=base / rel)
        unknown = sorted(set(fc.requirement_ids) - req_ids)
        if unknown:
            raise PlanningError("unknown-file-requirement", f"{rel} references unknown requirements {unknown}")
        file_changes.append(fc)

    targets = [fc.path for fc in file_changes]
    if len(targets) != len(set(targets)):
        raise PlanningError("duplicate-file-target", "Plan file realization targets must be unique")
    target_set = set(targets)
    for fc in file_changes:
        missing_deps = sorted(set(fc.depends_on_paths) - target_set)
        if missing_deps:
            raise PlanningError("unresolved-file-dependency", f"{fc.path} depends on unplanned paths {missing_deps}")

    for fc in file_changes:
        existed = _exists_at(repository, predecessor, fc.path)
        if fc.operation == "create" and existed:
            raise PlanningError("impossible-create", f"{fc.path} already exists at implementation predecessor")
        if fc.operation in {"modify", "delete", "regenerate"} and not existed:
            raise PlanningError("impossible-existing-operation", f"{fc.operation} target absent at predecessor: {fc.path}")

    execution_rel = _plan_relative(docs["execution"])
    invariants_rel = _plan_relative(docs["invariants"])
    validation_rel = _plan_relative(docs["validation"])
    completion_rel = _plan_relative(docs["completion"])

    execution = _common_document(resolved[execution_rel], artifact_type="plan-execution", plan_id=plan_id, path=base / execution_rel)
    invariants = _common_document(resolved[invariants_rel], artifact_type="plan-invariants", plan_id=plan_id, path=base / invariants_rel)
    validation = _common_document(resolved[validation_rel], artifact_type="plan-validation", plan_id=plan_id, path=base / validation_rel)
    completion = _common_document(resolved[completion_rel], artifact_type="plan-completion", plan_id=plan_id, path=base / completion_rel)

    validation_ids = {v.get("id") for v in validation.get("validation", []) if isinstance(v, dict)}
    for fc in file_changes:
        unknown = sorted(set(fc.validation_ids) - validation_ids)
        if unknown:
            raise PlanningError("unknown-file-validation", f"{fc.path} references unknown validation IDs {unknown}")

    return LogicalPlan(
        plan_id,
        pmeta.get("title", ""),
        pmeta.get("description", ""),
        normalize_repo_path(plan_path.as_posix()),
        predecessor,
        functional_set,
        requirements,
        tuple(file_changes),
        execution,
        invariants,
        validation,
        completion,
    )
