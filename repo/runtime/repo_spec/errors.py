from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(eq=False)
class RepoSpecError(Exception):
    code: str
    message: str
    owning_phase: str
    artifact: str | None = None
    path: str | None = None
    context: dict[str, Any] | None = None
    def __str__(self) -> str:
        parts = [f"{self.owning_phase}:{self.code}", self.message]
        if self.artifact: parts.append(f"artifact={self.artifact}")
        if self.path: parts.append(f"path={self.path}")
        return " | ".join(parts)

class DesignError(RepoSpecError):
    def __init__(self, code: str, message: str, **kw: Any): super().__init__(code, message, "Design", **kw)
class PlanningError(RepoSpecError):
    def __init__(self, code: str, message: str, **kw: Any): super().__init__(code, message, "Planning", **kw)
class ConformanceError(RepoSpecError):
    def __init__(self, code: str, message: str, **kw: Any): super().__init__(code, message, "Conformance", **kw)
class AssuranceError(RepoSpecError):
    def __init__(self, code: str, message: str, **kw: Any): super().__init__(code, message, "Assurance", **kw)
class BuildError(RepoSpecError):
    def __init__(self, code: str, message: str, **kw: Any): super().__init__(code, message, "Build", **kw)
class GovernanceError(RepoSpecError):
    def __init__(self, code: str, message: str, **kw: Any): super().__init__(code, message, "Governance", **kw)

def route_defect(exc: RepoSpecError) -> str:
    return exc.owning_phase
