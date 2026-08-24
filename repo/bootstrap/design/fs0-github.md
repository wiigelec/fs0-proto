# FS0 GitHub Remote Operating Profile

## Status

Part of the non-authoritative FS0-Core Bootstrap Design Proposal.

Read `fs0-design.md` first. This chunk does not independently create authority.

---

# FS0.7 — GitHub Remote Operating Profile

## Purpose

Provide the minimum GitHub realization necessary for FS0 to be operated end to end without access to a contributor's local filesystem.

GitHub is the required initial operating platform for FS0.

GitHub does not define Governance, Conformance, or Assurance semantics.

It realizes those semantics.

## Required Remote Capabilities

FS0 shall be operable through the GitHub remote for:

- repository state inspection;
- file and artifact reads;
- governed artifact creation and update;
- stable governed-work identity;
- candidate branch or commit identity;
- candidate review;
- canonical remote Conformance execution;
- remote Assurance evidence and findings;
- explicit stage acceptance representation;
- exact candidate revision resolution;
- merge or equivalent accepted-state publication; and
- accepted repository-state resolution.

## Bootstrap GitHub Realization

FS0 may use GitHub-native mechanisms such as:

- issues;
- branches;
- commits;
- pull requests;
- Actions;
- comments or reviews; and
- repository files.

The allowed GitHub mechanism set above is implementation latitude only; the normative FS0 mapping is fixed by the binding below.

No GitHub mechanism gains framework authority merely because FS0 uses it.

## GitHub Capability and Credential Contract

The user is responsible for establishing Git and GitHub authentication before bootstrap.

Bootstrap and post-cutover FS0 shall verify only that the acting identity can perform the technical capabilities required by the intended operation.

Required capability classes include:

```text
repository metadata read
repository content read
repository content write
Git ref read
Git ref create/update
issue read
issue create/update/comment
pull-request read
pull-request create/update
workflow/check read
workflow execution through repository events
commit/status evidence read
authenticated actor identity resolution
```

Authentication secrets, tokens, private keys, and equivalent credentials shall remain external to repository-maintained state.

A missing required capability shall block the operation.

Technical write permission is capability only and shall not enlarge Governance authorization.

## FS0 GitHub Binding

The initial GitHub realization is fixed for FS0 bootstrap and first self-hosted operation.

The mapping is:

| Framework concept | FS0 GitHub realization |
| --- | --- |
| Design Proposal | maintained repository file |
| Design governed work | GitHub issue |
| Plan governed work | separate GitHub issue |
| Build governed work | separate GitHub issue |
| candidate repository state | Git branch and exact commit SHA |
| candidate review surface | pull request |
| canonical Conformance execution | GitHub Actions workflow |
| Conformance evidence | workflow/check result tied to exact candidate SHA |
| Assurance review case | structured maintained repository artifact |
| Assurance finding | structured maintained repository artifact, optionally referenced in GitHub discussion |
| Design/Plan/Build stage acceptance | structured machine-readable GitHub issue comment on the governed-work issue |
| bootstrap provenance | dedicated GitHub issue created by the external bootstrap process |
| bootstrap acceptance | structured machine-readable comment on the bootstrap provenance issue identifying the exact FS0 candidate commit |
| accepted repository state | dedicated `refs/heads/main` Git ref plus matching acceptance record |

GitHub issue, pull-request, merge, review, comment, or workflow state shall not independently create Governance acceptance.

GitHub provides identity, collaboration, execution, and publication surfaces.

Framework semantics remain defined by accepted FS0 authority.

## Required Remote Questions

FS0 must make these questions answerable from repository/GitHub state without relying on chat history:

1. What revision is currently accepted?
2. What Design work is active?
3. What Design Proposal initiated it?
4. What normative delta is the candidate or accepted Design result?
5. What Plan is accepted?
6. What Build work is authorized?
7. What exact revision is under review?
8. What Conformance evidence applies to that revision?
9. What Assurance cases and findings apply to that revision?
10. Has the candidate been explicitly accepted?
11. What resulting revision became accepted?
12. What work remains unauthorized?

## Minimum GitHub State Management

FS0 shall distinguish:

```text
repository content
desired GitHub operating state
observed GitHub state
authorized mutation
verified resulting state
```

However, FS0 does not need to govern all GitHub settings.

## Deferred GitHub Capabilities

FS0 shall defer unless strictly required for safe bootstrap operation:

- generalized hosting-platform profile framework;
- branch-protection management;
- repository ruleset management;
- merge queues;
- comprehensive label management;
- repository settings management;
- generalized rollback framework;
- generated issue forms;
- generated pull-request templates;
- full remote desired-state management; and
- support for hosting platforms other than GitHub.

---

---

# FS0.8 — Bootstrap Installation and Cutover

## Purpose

Create the one accepted FS0 state from which all later framework evolution becomes self-hosted.

## Bootstrap Sequence

The bootstrap sequence shall be:

1. verify the user-supplied target Git repository, GitHub remote, authentication, and required technical capabilities;
2. construct the FS0 candidate from this non-authoritative bootstrap Design input and the canonical bootstrap realization inputs resolved from repository state;
3. install candidate FS0 maintained artifacts;
4. generate required orientation and license surfaces;
5. install the minimum candidate GitHub operating profile;
6. publish the candidate through the existing user-supplied Git/GitHub environment;
7. execute candidate mechanical checks as bootstrap verification evidence;
8. perform external semantic audit as bootstrap audit evidence;
9. correct defects in Design input or bootstrap realization as appropriate;
10. repeat until the candidate satisfies FS0 bootstrap criteria;
11. create the dedicated bootstrap provenance issue and structured bootstrap acceptance comment for one exact candidate revision;
12. create `refs/heads/main` at that exact accepted revision and verify it against the bootstrap acceptance record;
13. create the one-way bootstrap cutover marker;
14. treat FS0 Governance, Conformance, and Assurance as authoritative operating mechanisms only after that cutover;
15. disable further use of bootstrap authority for ordinary framework evolution.

## One-Way Cutover Marker

FS0 shall maintain a machine-resolvable bootstrap cutover record.

The cutover record shall identify at least:

```text
cutover state
first accepted FS0 revision
bootstrap acceptance record
accepted Git ref
cutover timestamp
```

The only valid bootstrap lifecycle is:

```text
candidate
→ cutover
```

There is no transition from `cutover` back to bootstrap candidate mode.

After `cutover`:

- bootstrap authority shall remain exhausted;
- authoritative determination shall use accepted authoritative read surfaces rather than non-authoritative bootstrap maintenance source;
- bootstrap maintenance machinery may be used only within FS0 Governance-authorized work;
- bootstrap maintenance machinery shall not independently create acceptance; and
- ordinary framework evolution shall occur only through FS0 Governance.

## Bootstrap Artifact Status

Bootstrap Design artifacts remain non-authoritative provenance.

Bootstrap source data, templates, and generators may remain active FS0 maintenance state after cutover.

They shall not become authoritative read surfaces or independent authorization paths.

## Cutover Invariant

**After FS0 cutover, every persistent framework change SHALL occur through FS0 Governance, and no bootstrap-only mechanism SHALL independently create accepted framework state.**

---
