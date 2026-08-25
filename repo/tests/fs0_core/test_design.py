from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from repo_spec.design import parse_design, resolve_design_inputs
from repo_spec.errors import DesignError
from repo_spec.repository import Repository


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=True)
    return p.stdout.strip()


def init_repo() -> tuple[tempfile.TemporaryDirectory, Path]:
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    git(root, "init")
    git(root, "config", "user.email", "fs0@example.invalid")
    git(root, "config", "user.name", "FS0 Test")
    return td, root


class DesignTests(unittest.TestCase):
    def test_block_sequence_metadata_and_statement_identity(self):
        text = """---
doc_id: DP-020
artifact_type: design-proposal
canonical_format: markdown
depends_on:
  - DP-010
---

**DP020-DETAIL-001**
A thing SHALL exist.
"""
        proposal = parse_design(text, path="repo/proposals/governance.md", revision="a" * 40)
        self.assertEqual(proposal.doc_id, "DP-020")
        self.assertEqual(proposal.depends_on, ("DP-010",))
        self.assertEqual(proposal.statement_ids(), {"DP020-DETAIL-001"})

    def test_malformed_header_fails(self):
        with self.assertRaises(DesignError):
            parse_design(
                "doc_id: DP-001\n",
                path="repo/proposals/bad.md",
                revision="a" * 40,
            )

    def test_duplicate_statement_fails(self):
        text = """---
doc_id: DP-001
artifact_type: design-proposal
canonical_format: markdown
depends_on: []
---

**DP001-DETAIL-001**
One.

**DP001-DETAIL-001**
Two.
"""
        with self.assertRaises(DesignError):
            parse_design(text, path="repo/proposals/a.md", revision="a" * 40)

    def test_wrong_statement_ownership_fails(self):
        text = """---
doc_id: DP-001
artifact_type: design-proposal
canonical_format: markdown
depends_on: []
---

**DP002-DETAIL-001**
Wrong owner.
"""
        with self.assertRaises(DesignError):
            parse_design(text, path="repo/proposals/a.md", revision="a" * 40)

    def test_exact_revision_binding_is_preserved(self):
        td, root = init_repo()
        self.addCleanup(td.cleanup)
        proposals = root / "repo/proposals"
        proposals.mkdir(parents=True)
        path = proposals / "a.md"
        path.write_text("""---
doc_id: DP-001
artifact_type: design-proposal
canonical_format: markdown
depends_on: []
---

**DP001-DETAIL-001**
Original.
""")
        git(root, "add", ".")
        git(root, "commit", "-m", "original")
        original = git(root, "rev-parse", "HEAD")

        path.write_text(path.read_text().replace("Original.", "Later."))
        git(root, "add", ".")
        git(root, "commit", "-m", "later")

        repo = Repository(root)
        index = resolve_design_inputs(repo, [{
            "doc_id": "DP-001",
            "path": "repo/proposals/a.md",
            "revision": original,
            "statements": ["DP001-DETAIL-001"],
        }])
        proposal = index.by_doc_id()["DP-001"]
        self.assertEqual(proposal.revision, original)
        self.assertIn("Original.", repo.read_text_at(original, proposal.path))
        self.assertNotIn("Later.", repo.read_text_at(original, proposal.path))

    def test_unresolved_dependency_fails(self):
        td, root = init_repo()
        self.addCleanup(td.cleanup)
        proposals = root / "repo/proposals"
        proposals.mkdir(parents=True)
        (proposals / "a.md").write_text("""---
doc_id: DP-001
artifact_type: design-proposal
canonical_format: markdown
depends_on:
  - DP-002
---

**DP001-DETAIL-001**
Original.
""")
        git(root, "add", ".")
        git(root, "commit", "-m", "design")
        rev = git(root, "rev-parse", "HEAD")
        repo = Repository(root)
        with self.assertRaises(DesignError):
            resolve_design_inputs(repo, [{
                "doc_id": "DP-001",
                "path": "repo/proposals/a.md",
                "revision": rev,
                "statements": ["DP001-DETAIL-001"],
            }])


if __name__ == "__main__":
    unittest.main()
