from __future__ import annotations
import hashlib, json, re
from pathlib import Path, PurePosixPath
from typing import Any
from .errors import PlanningError

_SHA40 = re.compile(r"^[0-9a-f]{40}$")

def _no_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise PlanningError("duplicate-json-key", f"duplicate JSON key: {key}")
        obj[key] = value
    return obj

def loads_json(text: str, *, artifact: str | None = None) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_no_duplicates)
    except PlanningError:
        raise
    except json.JSONDecodeError as exc:
        raise PlanningError("invalid-json", f"line {exc.lineno} column {exc.colno}: {exc.msg}", artifact=artifact) from exc

def load_json(path: Path) -> Any:
    try:
        return loads_json(path.read_text(encoding="utf-8"), artifact=str(path))
    except OSError as exc:
        raise PlanningError("json-read-failed", str(exc), path=str(path)) from exc

def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def normalize_repo_path(value: str) -> str:
    if not value or "\\" in value:
        raise PlanningError("unsafe-path", f"invalid repository-relative path: {value!r}")
    p = PurePosixPath(value)
    if p.is_absolute() or any(part in ("", ".", "..") for part in p.parts):
        raise PlanningError("unsafe-path", f"invalid repository-relative path: {value!r}")
    return p.as_posix()

def resolve_repo_path(root: Path, value: str) -> Path:
    rel = normalize_repo_path(value)
    root = root.resolve()
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise PlanningError("path-escape", f"path escapes repository: {value}") from exc
    return candidate

def is_sha40(value: str) -> bool:
    return bool(_SHA40.fullmatch(value))

def require_sha40(value: str, *, field: str = "revision") -> str:
    if not is_sha40(value):
        raise PlanningError("invalid-revision", f"{field} must be lowercase 40-hex")
    return value

def content_sha256(data: bytes | str) -> str:
    if isinstance(data, str): data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()
