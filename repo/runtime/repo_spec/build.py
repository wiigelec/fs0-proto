"""Plan-bound Build authorization and mutation evidence."""

from __future__ import annotations
from dataclasses import dataclass

from .assurance import AssuranceReport, require_pass as require_assurance_pass
from .conformance import ConformanceReport, build_conformance, require_pass as require_conformance_pass
from .errors import BuildError
from .plan import LogicalPlan
from .repository import Repository

@dataclass
class BuildSession:
    repository: Repository
    plan: LogicalPlan
    build_id: str
    actor: str
    build_start_revision: str

    @classmethod
    def open(
        cls,
        repository: Repository,
        plan: LogicalPlan,
        *,
        build_id: str,
        actor: str,
        build_start_revision: str | None = None,
    ) -> "BuildSession":
        start = build_start_revision or repository.head
        repository.require_revision(start)
        pred = plan.implementation_predecessor
        if start != pred and not repository.artifact_only_between(pred, start):
            raise BuildError(
                "invalid-build-start",
                "Build start must equal the implementation predecessor or differ only by governed Design/Planning artifacts",
            )
        if not build_id or not actor:
            raise BuildError("invalid-build-identity", "Build requires stable build_id and actor")
        return cls(repository, plan, build_id, actor, start)

    def authorized(self, path: str, operation: str) -> bool:
        return any(fc.path == path and fc.operation == operation for fc in self.plan.file_changes)

    def require_authorized(self, path: str, operation: str) -> None:
        if not self.authorized(path, operation):
            raise BuildError("mutation-not-authorized", f"{operation} is not authorized for {path}", path=path)

    def observe_committed_mutations(self, resulting_revision: str | None = None) -> tuple[dict, ...]:
        end = resulting_revision or self.repository.head
        observed = []
        planned_paths = {fc.path for fc in self.plan.file_changes}
        for mutation in self.repository.changed_paths(self.plan.implementation_predecessor, end):
            artifact_only = (
                mutation.path.startswith("repo/proposals/")
                or mutation.path.startswith("repo/planning/")
            )
            if artifact_only and mutation.path not in planned_paths:
                continue
            self.require_authorized(mutation.path, mutation.operation)
            observed.append({"path": mutation.path, "operation": mutation.operation})
        return tuple(observed)

    def manifest(self, *, resulting_revision: str | None = None) -> dict:
        resulting = resulting_revision or self.repository.head
        mutations = list(self.observe_committed_mutations(resulting))
        return {
            "schema_version": "1",
            "artifact_type": "build-manifest",
            "build_id": self.build_id,
            "plan_id": self.plan.id,
            "actor": self.actor,
            "implementation_predecessor": self.plan.implementation_predecessor,
            "build_start_revision": self.build_start_revision,
            "resulting_revision": resulting,
            "mutations": mutations,
        }

    def finalize(
        self,
        *,
        conformance: ConformanceReport,
        assurance: AssuranceReport,
        resulting_revision: str | None = None,
    ) -> dict:
        manifest = self.manifest(resulting_revision=resulting_revision)
        local_report = build_conformance(self.plan, manifest)
        require_conformance_pass(local_report, subject_type="build", subject_id=self.build_id)
        require_conformance_pass(conformance)
        require_assurance_pass(assurance, phase="Build", subject_id=self.build_id)
        return manifest
