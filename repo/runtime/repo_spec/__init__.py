"""FS0-Core repo-spec runtime."""

from .errors import (
    AssuranceError, BuildError, ConformanceError, DesignError,
    GovernanceError, PlanningError, RepoSpecError,
)
from .repository import Repository
from .design import DesignIndex, DesignProposal, load_design_input
from .functional_set import FunctionalSet, load_functional_set

__all__ = [
    "RepoSpecError", "DesignError", "PlanningError", "ConformanceError",
    "AssuranceError", "BuildError", "GovernanceError", "Repository",
    "DesignIndex", "DesignProposal", "load_design_input",
    "FunctionalSet", "load_functional_set",
]
__version__ = "0.0.0"
