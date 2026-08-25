from __future__ import annotations

import unittest
from pathlib import Path

from repo_spec.assurance import make_report
from repo_spec.build import BuildSession
from repo_spec.conformance import build_conformance, plan_conformance
from repo_spec.errors import BuildError, GovernanceError
from repo_spec.governance import accept
from repo_spec.normative import AuthorizationGraph, Authority, Delegation
from repo_spec.repository import Repository


ROOT = Path(__file__).resolve().parents[3]
PLAN_PATH = ROOT / "repo/planning/000_FS0-CORE/plan.json"
PRE_BUILD = "06a0481ac6efd77e6da3b616854ee5602d6496cc"


class BuildGovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Repository(ROOT)
        cls.plan, cls.plan_conf = plan_conformance(cls.repo, str(PLAN_PATH))

    def test_build_session_opens_from_artifact_only_descendant(self):
        session = BuildSession.open(
            self.repo,
            self.plan,
            build_id="FS0-TEST-BUILD",
            actor="builder",
            build_start_revision=PRE_BUILD,
        )
        self.assertEqual(session.build_start_revision, PRE_BUILD)

    def test_default_deny_for_unplanned_mutation(self):
        session = BuildSession.open(
            self.repo, self.plan,
            build_id="FS0-TEST-BUILD", actor="builder",
            build_start_revision=PRE_BUILD,
        )
        self.assertTrue(session.authorized("repo/runtime/repo_spec/build.py", "create"))
        self.assertFalse(session.authorized("README.md", "modify"))
        with self.assertRaises(BuildError):
            session.require_authorized("README.md", "modify")

    def test_build_manifest_and_conformance(self):
        session = BuildSession.open(
            self.repo, self.plan,
            build_id="FS0-TEST-BUILD", actor="builder",
            build_start_revision=PRE_BUILD,
        )
        manifest = session.manifest(resulting_revision=self.repo.head)
        self.assertEqual(manifest["artifact_type"], "build-manifest")
        self.assertEqual(manifest["plan_id"], self.plan.id)
        self.assertGreater(len(manifest["mutations"]), 0)
        report = build_conformance(self.plan, manifest)
        self.assertTrue(report.passed)

    def test_unplanned_manifest_mutation_fails(self):
        with self.assertRaises(Exception):
            build_conformance(self.plan, {
                "schema_version": "1",
                "artifact_type": "build-manifest",
                "build_id": "BAD",
                "plan_id": self.plan.id,
                "actor": "builder",
                "implementation_predecessor": self.plan.implementation_predecessor,
                "build_start_revision": PRE_BUILD,
                "resulting_revision": self.repo.head,
                "mutations": [{"path": "README.md", "operation": "modify"}],
            })

    def test_missing_planned_manifest_mutation_fails(self):
        mutations = [
            {"path": fc.path, "operation": fc.operation}
            for fc in self.plan.file_changes[:-1]
        ]
        with self.assertRaises(Exception):
            build_conformance(self.plan, {
                "schema_version": "1",
                "artifact_type": "build-manifest",
                "build_id": "INCOMPLETE",
                "plan_id": self.plan.id,
                "actor": "builder",
                "implementation_predecessor": self.plan.implementation_predecessor,
                "build_start_revision": PRE_BUILD,
                "resulting_revision": self.repo.head,
                "mutations": mutations,
            })

    def test_non_circular_build_acceptance(self):
        conf = build_conformance(self.plan, {
            "schema_version": "1",
            "artifact_type": "build-manifest",
            "build_id": "FS0-TEST-BUILD",
            "plan_id": self.plan.id,
            "actor": "builder",
            "implementation_predecessor": self.plan.implementation_predecessor,
            "build_start_revision": PRE_BUILD,
            "resulting_revision": self.repo.head,
            "mutations": [
                {"path": fc.path, "operation": fc.operation}
                for fc in self.plan.file_changes
            ],
        })
        assurance = make_report(
            phase="Build",
            subject_id="FS0-TEST-BUILD",
            disposition="PASS",
            rationale="test",
        )
        graph = AuthorizationGraph(
            [Authority("accepted-plan"), Authority("governor")],
            [Delegation("accepted-plan", "governor", "accept:Build")],
        )
        record = accept(
            acceptance_id="ACC-TEST",
            stage="Build",
            subject_id="FS0-TEST-BUILD",
            actor="governor",
            predecessor_authority="accepted-plan",
            resulting_state=self.repo.head,
            authority_graph=graph,
            conformance=conf,
            assurance=assurance,
            evidence_refs=("conf:test", "assurance:test"),
        )
        self.assertEqual(record.decision, "ACCEPT")

    def test_circular_acceptance_fails(self):
        conf = build_conformance(self.plan, {
            "schema_version": "1",
            "artifact_type": "build-manifest",
            "build_id": "FS0-TEST-BUILD",
            "plan_id": self.plan.id,
            "actor": "builder",
            "implementation_predecessor": self.plan.implementation_predecessor,
            "build_start_revision": PRE_BUILD,
            "resulting_revision": self.repo.head,
            "mutations": [
                {"path": fc.path, "operation": fc.operation}
                for fc in self.plan.file_changes
            ],
        })
        assurance = make_report(
            phase="Build",
            subject_id="FS0-TEST-BUILD",
            disposition="PASS",
            rationale="test",
        )
        graph = AuthorizationGraph(
            [Authority("accepted-plan"), Authority("governor")],
            [Delegation("accepted-plan", "governor", "accept:Build")],
        )
        with self.assertRaises(GovernanceError):
            accept(
                acceptance_id="ACC-CIRC",
                stage="Build",
                subject_id="FS0-TEST-BUILD",
                actor="governor",
                predecessor_authority="accepted-plan",
                resulting_state="accepted-plan",
                authority_graph=graph,
                conformance=conf,
                assurance=assurance,
                evidence_refs=("conf:test", "assurance:test"),
            )

    def test_evidence_schema_contract_shapes(self):
        import json
        import re

        planning = ROOT / "repo/planning"
        assurance = json.loads((planning / "assurance-report.schema.json").read_text())
        conformance = json.loads((planning / "conformance-report.schema.json").read_text())
        manifest = json.loads((planning / "build-manifest.schema.json").read_text())
        acceptance = json.loads((planning / "acceptance.schema.json").read_text())

        for schema in (assurance, conformance, manifest, acceptance):
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertEqual(schema["type"], "object")
            self.assertFalse(schema["additionalProperties"])
            self.assertTrue(schema["required"])

        path_pattern = manifest["properties"]["mutations"]["items"]["properties"]["path"]["pattern"]
        self.assertIsNotNone(re.fullmatch(path_pattern, "repo/runtime/good.py"))
        self.assertIsNone(re.fullmatch(path_pattern, "../escape"))
        self.assertIsNone(re.fullmatch(path_pattern, "/absolute"))
        self.assertEqual(acceptance["properties"]["decision"]["const"], "ACCEPT")
        self.assertEqual(set(assurance["properties"]["disposition"]["enum"]), {"PASS", "FAIL"})
        self.assertEqual(set(conformance["properties"]["subject"]["properties"]["type"]["enum"]),
                         {"design", "functional-set", "plan", "build"})


if __name__ == "__main__":
    unittest.main()
