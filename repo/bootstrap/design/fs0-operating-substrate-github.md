# FS0 Operating Substrate and GitHub

## Status

Part of the non-authoritative FS0-Core Bootstrap Design Proposal.

Read `fs0-design.md` first. This chunk does not independently create authority.

---

# Bootstrap Repository

The disposable bootstrap repository is initially expected to contain:

```text
fs0-proto/
└── repo/
    └── bootstrap/
        ├── design/
        └── scripts/
```

Before repository initialization, this skeleton is only bootstrap construction state.

The initial FS0 Design Proposal belongs at:

```text
repo/bootstrap/design/fs0-design.md
```

Bootstrap construction scripts belong at:

```text
repo/bootstrap/scripts/
```

These bootstrap paths are temporary construction surfaces.

They do not automatically become permanent successor-framework namespaces.

FS0 Design shall decide which installed artifacts become maintained framework state and which bootstrap artifacts remain historical or disposable.

---

---

# Bootstrap Principle

FS0 cannot authorize its own initial existence.

Therefore one explicit external bootstrap exception is required.

Before cutover, the bootstrap process operates outside FS0 Governance authority.

Pre-cutover execution of candidate FS0 mechanisms produces bootstrap verification evidence only.

It shall not be represented as governed FS0 Conformance, governed FS0 Assurance, or FS0 Governance acceptance before the first FS0 state is accepted.

The bootstrap mechanism may:

- construct the initial FS0 candidate;
- initialize the Git repository;
- create the GitHub repository;
- publish the initial candidate;
- install the minimum GitHub operating profile;
- run initial bootstrap mechanical verification;
- run external bootstrap semantic audit;
- correct bootstrap defects; and
- explicitly accept one exact repository revision as the first FS0 operating state.

After initial FS0 acceptance, bootstrap authority is exhausted.

The bootstrap mechanism shall not remain an alternate path for ordinary framework evolution.

All subsequent persistent framework change shall occur through FS0 Governance.

---

---

# FS0.6 — Operating Substrate

## Purpose

Provide the minimum execution, Git, network, authentication, privileged-mutation, and repository-orientation capabilities required for FS0 to build and evolve itself after the external bootstrap environment is removed.

FS0 should be understood like a minimal base operating-system installation: deliberately small, but already capable of acquiring, building, installing, verifying, and publishing the rest of the system.

Minimality shall not be achieved by removing capabilities required for self-hosting.

## Required Local and Remote Tooling Capabilities

The FS0 operating environment shall provide access to:

- Git repository inspection;
- Git branch, commit, ref, fetch, pull, and push operations;
- HTTPS/TLS network access;
- DNS/network resolution as required by GitHub;
- authenticated GitHub API access;
- GitHub issue, branch, pull-request, comment/review, ref, and workflow operations required by the FS0 GitHub binding;
- execution of FS0-maintained scripts and Conformance commands;
- retrieval of remote Conformance evidence; and
- publication of accepted state.

These are operating capabilities, not independent authority.

## Governed Privileged Mutation

FS0 requires the repository-framework equivalent of privilege escalation.

An actor or automation may possess technical credentials capable of changing repository or GitHub state, but possession of those credentials does not grant Governance authority.

Privileged mutation shall follow:

```text
accepted authority
→ accepted Plan
→ authorized Build
→ bounded privileged mutation
→ verification
→ explicit acceptance
```

A privileged mutation capability shall be usable only within the scope authorized by the applicable governed Build work.

Technical write access shall not authorize adjacent, unrelated, or successor work.

## Self-Modification

After cutover, FS0 shall be capable of:

- reading its accepted authority;
- proposing a bounded change;
- establishing accepted Design authority;
- establishing an accepted Plan;
- creating and publishing candidate repository state;
- changing its own maintained framework implementation when authorized;
- changing its own GitHub realization when authorized;
- executing remote Conformance against the candidate;
- recording required Assurance findings;
- explicitly accepting or rejecting the candidate; and
- publishing the resulting accepted repository state.

No step in this sequence may require the external bootstrap environment.

## Network Sufficiency

GitHub access is part of the initial FS0 operating substrate.

The installed FS0 shall have enough authenticated network capability to read and mutate every GitHub object used by the FS0 GitHub binding, subject to Governance authorization.

Networking is operational substrate.

GitHub-specific semantics remain subordinate to portable FS0 authority.

## Repository Orientation Surfaces

The root of the FS0 repository shall contain:

```text
README.md
AGENTS.md
LICENSE
```

### `README.md`

`README.md` shall provide a concise human-readable entry point containing:

- repository purpose;
- current bootstrap/cutover status;
- Design Proposal index;
- accepted-state discovery guidance;
- basic repository operation guidance; and
- a clear statement that implementation and GitHub state do not independently create authority.

### `AGENTS.md`

`AGENTS.md` shall provide a concise AI-agent initialization contract containing:

- required initial reading order;
- how to locate the relevant Design chunk;
- how to determine whether the repository is pre-cutover or post-cutover;
- how to resolve accepted state after cutover;
- the prohibition against treating technical write capability as authority;
- the requirement to inspect exact GitHub candidate/evidence state before mutation; and
- the rule that after cutover all persistent framework mutation routes through FS0 Governance.

`AGENTS.md` is an operational orientation surface.

It shall remain subordinate to accepted authority and shall not become a second semantic owner.

### `LICENSE`

FS0 shall carry an explicit repository license from the initial published prototype state.

The bootstrap prototype shall use GNU General Public License version 3, matching the originating repo-spec project, unless later accepted Governance changes the licensing decision where legally permitted.

## Bootstrap Independence

After cutover, routine self-hosting shall remain possible if the external bootstrap scripts are unavailable.

Bootstrap scripts may remain as historical provenance, but FS0's ability to build FS1 and later functional sets shall depend only on installed FS0 capabilities and ordinary external services explicitly included in its operating substrate, such as GitHub.

## Operating-Substrate Acceptance Test

FS0 operating substrate is sufficient only if an authorized agent operating through the GitHub remote can:

1. discover repository purpose and operating rules from `README.md` and `AGENTS.md`;
2. resolve current accepted state;
3. inspect controlling authority and governed work;
4. create bounded candidate work;
5. publish candidate repository changes;
6. execute and inspect remote Conformance;
7. create or inspect required Assurance state;
8. perform authorized privileged GitHub mutations;
9. record explicit acceptance; and
10. publish the successor accepted state without access to the bootstrap environment.

---

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
- accepted main-state resolution.

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
| bootstrap acceptance | externally attributable structured GitHub record identifying the exact FS0 candidate commit |
| accepted repository state | dedicated `refs/heads/accepted` Git ref plus matching acceptance record |

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

1. construct the FS0 candidate from this non-authoritative bootstrap Design input;
2. initialize the disposable Git repository;
3. install candidate FS0 maintained artifacts;
4. install the minimum candidate GitHub operating profile;
5. create the GitHub remote repository;
6. publish the candidate;
7. execute candidate mechanical checks as bootstrap verification evidence;
8. perform external semantic audit as bootstrap audit evidence;
9. correct defects in Design input or bootstrap realization as appropriate;
10. repeat until the candidate satisfies FS0 bootstrap criteria;
11. create the externally attributable structured bootstrap acceptance record for one exact candidate revision;
12. create `refs/heads/accepted` at that exact accepted revision and verify it against the bootstrap acceptance record;
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

- bootstrap construction scripts shall refuse ordinary framework mutation;
- bootstrap scripts may be inspected for provenance;
- bootstrap scripts may be used only for explicitly authorized disaster-recovery or reconstruction work defined by later accepted authority; and
- ordinary framework evolution shall occur only through FS0 Governance.

## Bootstrap Artifact Status

Bootstrap scripts and Design artifacts may remain in history for provenance.

They shall not automatically remain active framework authority or ordinary mutation paths after cutover.

## Cutover Invariant

**After FS0 cutover, every persistent framework change SHALL occur through FS0 Governance, and no bootstrap-only mechanism SHALL independently create accepted framework state.**

---
