from __future__ import annotations

import json
import unittest
from pathlib import Path

from repo_spec.assurance import make_report
from repo_spec.cli import build_parser
from repo_spec.conformance import ConformanceReport
from repo_spec.errors import GovernanceError
from repo_spec.governance import accept
from repo_spec.normative import AuthorizationGraph, Authority, Delegation

ROOT = Path(__file__).resolve().parents[2]

class DesignAcceptanceTests(unittest.TestCase):
    def _conformance(self):
        return ConformanceReport(
            "CONF-DESIGN-DP-900", "design-proposal", "DP-900", "PASS",
            ("evidence:design-conformance",), (),
        )

    def _assurance(self):
        return make_report(
            phase="Design",
            subject_id="DP-900",
            disposition="PASS",
            rationale="The candidate Design Proposal is semantically ready for Planning.",
            evidence_refs=("evidence:design-assurance",),
        )

    def test_authorized_design_acceptance(self):
        graph = AuthorizationGraph(
            [Authority("accepted-framework"), Authority("governor")],
            [Delegation("accepted-framework", "governor", "accept:Design")],
        )
        record = accept(
            acceptance_id="DESIGN-ACCEPT-900",
            stage="Design",
            subject_id="DP-900",
            actor="governor",
            predecessor_authority="accepted-framework",
            resulting_state="planning-ready:DP-900@candidate",
            authority_graph=graph,
            conformance=self._conformance(),
            assurance=self._assurance(),
            evidence_refs=("evidence:design-conformance", "evidence:design-assurance"),
        )
        self.assertEqual(record.decision, "ACCEPT")
        self.assertEqual(record.stage, "Design")
        self.assertNotEqual(record.resulting_state, record.predecessor_authority)

    def test_design_acceptance_requires_authority(self):
        graph = AuthorizationGraph([Authority("accepted-framework"), Authority("governor")], [])
        with self.assertRaises(GovernanceError):
            accept(
                acceptance_id="DESIGN-ACCEPT-900",
                stage="Design",
                subject_id="DP-900",
                actor="governor",
                predecessor_authority="accepted-framework",
                resulting_state="planning-ready:DP-900@candidate",
                authority_graph=graph,
                conformance=self._conformance(),
                assurance=self._assurance(),
                evidence_refs=("evidence:design-conformance", "evidence:design-assurance"),
            )

    def test_acceptance_schema_allows_design(self):
        schema = json.loads((ROOT / "planning/acceptance.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["stage"]["enum"], ["Design", "Planning", "Build"])

    def test_cli_exposes_design_accept(self):
        args = build_parser().parse_args([
            "design-accept",
            "--acceptance-id", "A",
            "--subject", "DP-900",
            "--actor", "governor",
            "--authority", "accepted-framework",
            "--authority-state", "authority.json",
            "--resulting-state", "planning-ready:DP-900@candidate",
            "--conformance", "conf.json",
            "--assurance", "assurance.json",
            "--evidence", "conf.json",
            "--output", "acceptance.json",
        ])
        self.assertEqual(args.acceptance_stage, "Design")

if __name__ == "__main__":
    unittest.main()
