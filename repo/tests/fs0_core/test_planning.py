from __future__ import annotations

import json
import unittest
from pathlib import Path

from repo_spec.assurance import make_report, require_pass
from repo_spec.errors import AssuranceError, GovernanceError, PlanningError
from repo_spec.normative import AuthorizationGraph, Authority, parse_requirement
from repo_spec.plan import load_plan
from repo_spec.repository import Repository


ROOT = Path(__file__).resolve().parents[3]
PLAN = ROOT / "repo/planning/000_FS0-CORE/plan.json"


class PlanningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Repository(ROOT)
        cls.plan = load_plan(PLAN, cls.repo)

    def test_current_plan_is_closed_and_executable(self):
        self.assertEqual(self.plan.id, "FS0-CORE-PLAN")
        self.assertEqual(self.plan.functional_set.id, "FS0-CORE")
        self.assertEqual(len(self.plan.requirements), 121)
        self.assertEqual(len(self.plan.file_changes), 24)
        self.assertEqual(len({f.path for f in self.plan.file_changes}), 24)

    def test_normative_force_ignores_inline_code_vocabulary(self):
        req = parse_requirement({
            "id": "FS0-NR-999",
            "statement": "A probe SHALL recognize `SHALL`, `SHALL NOT`, or `MAY` as vocabulary.",
            "evaluation": {
                "conformance": {"applicability": "required"},
                "assurance": {"applicability": "none", "rationale": "mechanical"},
            },
        })
        self.assertEqual(req.id, "FS0-NR-999")

    def test_multiple_operative_forces_fail(self):
        with self.assertRaises(PlanningError):
            parse_requirement({
                "id": "FS0-NR-999",
                "statement": "A probe SHALL exist and MAY disappear.",
                "evaluation": {
                    "conformance": {"applicability": "required"},
                    "assurance": {"applicability": "none", "rationale": "mechanical"},
                },
            })

    def test_none_assurance_requires_rationale(self):
        with self.assertRaises(PlanningError):
            parse_requirement({
                "id": "FS0-NR-999",
                "statement": "A probe SHALL exist.",
                "evaluation": {
                    "conformance": {"applicability": "required"},
                    "assurance": {"applicability": "none"},
                },
            })

    def test_planning_assurance_is_subject_bound(self):
        report = make_report(
            phase="Planning",
            subject_id=self.plan.id,
            disposition="PASS",
            rationale="test",
        )
        require_pass(report, phase="Planning", subject_id=self.plan.id)
        with self.assertRaises(AssuranceError):
            require_pass(report, phase="Build", subject_id=self.plan.id)

    def test_default_deny_without_delegation(self):
        graph = AuthorizationGraph([Authority("governance"), Authority("builder")])
        self.assertTrue(graph.authorized("governance", "accept:Planning", authority="governance"))
        self.assertFalse(graph.authorized("builder", "accept:Planning", authority="governance"))
        with self.assertRaises(GovernanceError):
            graph.require("builder", "accept:Planning", authority="governance")

    def test_plan_reference_graph_matches_declared_documents(self):
        plan_doc = json.loads(PLAN.read_text())
        docs = plan_doc["documents"]
        declared = {
            docs["requirements"], docs["execution"], docs["invariants"],
            docs["validation"], docs["completion"], *docs["file_plans"],
        }
        base = PLAN.parent
        actual = {
            p.relative_to(base).as_posix()
            for p in base.rglob("*.json")
            if p.name not in {"functional-set.json", "plan.json"}
        }
        self.assertEqual(actual, declared)


if __name__ == "__main__":
    unittest.main()
