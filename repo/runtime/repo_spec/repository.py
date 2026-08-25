from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import subprocess
from .errors import BuildError, DesignError
from .jsonio import normalize_repo_path, require_sha40

@dataclass(frozen=True)
class Mutation:
    path: str
    operation: str

class Repository:
    def __init__(self, root):
        self.root = Path(root).resolve()
        if not (self.root / ".git").exists():
            raise BuildError("not-git-repository", "explicit root is not a Git worktree", path=str(self.root))

    def _git(self, *args, check=True):
        p = subprocess.run(["git","-C",str(self.root),*args], text=True, capture_output=True)
        if check and p.returncode:
            raise BuildError("git-command-failed", p.stderr.strip() or p.stdout.strip() or "git failed")
        return p

    @property
    def head(self):
        return require_sha40(self._git("rev-parse","HEAD").stdout.strip().lower(), field="HEAD")

    def revision_exists(self, revision):
        require_sha40(revision)
        return self._git("cat-file","-e",f"{revision}^{{commit}}",check=False).returncode == 0

    def require_revision(self, revision):
        require_sha40(revision)
        if not self.revision_exists(revision):
            raise DesignError("missing-revision", f"missing Git revision: {revision}")
        return revision

    def read_text_at(self, revision, repo_path):
        self.require_revision(revision)
        repo_path = normalize_repo_path(repo_path)
        p = self._git("show",f"{revision}:{repo_path}",check=False)
        if p.returncode:
            raise DesignError("revision-path-unavailable", p.stderr.strip() or "path unavailable", path=repo_path)
        return p.stdout

    def is_ancestor(self, ancestor, descendant):
        self.require_revision(ancestor); self.require_revision(descendant)
        return self._git("merge-base","--is-ancestor",ancestor,descendant,check=False).returncode == 0

    def changed_paths(self, base, head=None):
        self.require_revision(base); head = head or self.head; self.require_revision(head)
        p = self._git("diff","--name-status","--find-renames",base,head)
        out = []
        for line in p.stdout.splitlines():
            if not line: continue
            f = line.split("\t"); s = f[0]
            if s.startswith("R"):
                out += [Mutation(normalize_repo_path(f[1]),"delete"), Mutation(normalize_repo_path(f[2]),"create")]
            else:
                out.append(Mutation(normalize_repo_path(f[-1]), {"A":"create","M":"modify","D":"delete"}.get(s[0],"modify")))
        return out

    def artifact_only_between(self, predecessor, build_start=None, artifact_roots=("repo/proposals/","repo/planning/")):
        start = build_start or self.head
        if not self.is_ancestor(predecessor, start):
            raise BuildError("predecessor-not-ancestor", "implementation predecessor is not an ancestor of Build start")
        return all(any(m.path.startswith(r) for r in artifact_roots) for m in self.changed_paths(predecessor,start))
