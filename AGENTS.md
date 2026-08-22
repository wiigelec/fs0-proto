# FS0 Agent Initialization

This repository is a disposable FS0 bootstrap prototype.

Before any repository mutation:

1. Read `README.md`.
2. Read `repo/bootstrap/design/fs0-design.md`.
3. Load only the design chunk or chunks relevant to the current operation.
4. Inspect the exact Git branch, commit, remote state, open governed-work issues, pull requests, workflow evidence, and acceptance state relevant to the proposed mutation.
5. Determine whether the repository is pre-cutover or post-cutover.

## Pre-cutover

Before cutover, FS0 is candidate implementation only.

Candidate Conformance execution is bootstrap verification evidence, candidate semantic review is bootstrap audit evidence, and neither is governed FS0 Conformance or Assurance yet.

Bootstrap changes must remain within the explicit FS0 bootstrap Design Proposal.

## Post-cutover

After cutover:

- resolve accepted repository state from `refs/heads/accepted` and its matching explicit acceptance record;
- identify the governing Design, Plan, and Build work for any persistent framework mutation;
- do not infer authority from merge state, issue closure, workflow success, implementation behavior, generated artifacts, or prior convention;
- treat technical GitHub write permission as capability, not authority;
- perform privileged mutation only within the bounded scope of accepted Governance authorization; and
- route persistent framework change through FS0 Governance.

## Authority boundary

`README.md` and `AGENTS.md` are operational orientation surfaces.

They are subordinate to accepted FS0 authority and must not be treated as independent semantic owners.

If repository state and controlling authority disagree, stop mutation and surface the conflict.
