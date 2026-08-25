from __future__ import annotations

import os
import unittest
from pathlib import Path

from repo_spec.conformance import plan_conformance
from repo_spec.evidence import (
    load_authorization_graph,
    require_evidence_refs,
    write_evidence,
)
from repo_spec.errors import GovernanceError
from repo_spec.repository import Repository
from repo_spec.validation import run_plan_validations


ROOT = Path(__file__).resolve().parents[3]
PLAN = ROOT / "repo/planning/000_FS0-CORE/plan.json"


class SuccessorCycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Repository(ROOT)
        cls.plan, _ = plan_conformance(cls.repo, str(PLAN))

    def test_authority_state_is_loaded_not_manufactured(self):
        rel = "repo/evidence/test-authority-state.json"
        path = ROOT / rel
        value = {
            "schema_version": "1",
            "artifact_type": "authority-state",
            "authorities": ["accepted-plan", "governor", "builder"],
            "delegations": [
                {
                    "source": "accepted-plan",
                    "target": "governor",
                    "capability": "accept:Build",
                }
            ],
        }
        try:
            write_evidence(ROOT, rel, value)
            graph = load_authorization_graph(ROOT, rel)
            self.assertTrue(
                graph.authorized(
                    "governor",
                    "accept:Build",
                    authority="accepted-plan",
                )
            )
            self.assertFalse(
                graph.authorized(
                    "builder",
                    "accept:Build",
                    authority="accepted-plan",
                )
            )
        finally:
            path.unlink(missing_ok=True)

    def test_durable_evidence_refs_resolve(self):
        rel = "repo/evidence/test-evidence.json"
        path = ROOT / rel
        try:
            write_evidence(
                ROOT,
                rel,
                {"schema_version": "1", "artifact_type": "test"},
            )
            self.assertEqual(require_evidence_refs(ROOT, [rel]), (rel,))
            with self.assertRaises(GovernanceError):
                require_evidence_refs(ROOT, ["repo/evidence/missing.json"])
        finally:
            path.unlink(missing_ok=True)

    def test_plan_mechanical_validations_execute(self):
        if os.environ.get("FS0_PLAN_VALIDATION_CHILD") == "1":
            return

        results = run_plan_validations(self.repo, self.plan)
        self.assertTrue(results)
        self.assertTrue(all(result.passed for result in results))
        self.assertTrue(
            all(result.kind in {"unit", "schema"} for result in results)
        )

    def test_build_session_has_no_manual_mutation_injection(self):
        from repo_spec.build import BuildSession

        self.assertFalse(hasattr(BuildSession, "record_mutation"))


if __name__ == "__main__":
    unittest.main()
