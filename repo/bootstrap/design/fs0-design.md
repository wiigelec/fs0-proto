# FS0-Core Bootstrap Design Proposal

## Status

Design proposal for the disposable `fs0-proto` bootstrap repository.

This document is non-authoritative bootstrap Design input.

It does not become accepted FS0 authority before cutover.

The one-time external bootstrap process may use this Design input to construct, audit, verify, and explicitly accept the first FS0 operating state.

Its purpose is to define the minimum end-to-end functional set required to install a self-hosting repository framework that can use its own Governance, Conformance, Assurance, and GitHub operating mechanisms to build the remainder of the successor repo-spec design.

FS0 is intentionally minimal.

Anything FS0 can correctly build after bootstrap should be deferred unless it is required for the first complete self-hosted remote lifecycle.

---

# 1. Objective

FS0-Core shall establish the smallest remotely operable framework capable of performing this complete loop:

**bootstrap seed**
→ **accepted FS0 authority**
→ **Design Proposal**
→ **Design**
→ **accepted normative authority**
→ **Plan**
→ **accepted realization intent**
→ **Build**
→ **Conformance**
→ **Assurance**
→ **Build acceptance**
→ **new accepted repository state**
→ **repeat without bootstrap authority**

FS0 succeeds when it can build and accept FS1 using only FS0-governed mechanisms operating against the GitHub remote.

---

# 2. Bootstrap Repository

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

# 3. Bootstrap Principle

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

# 4. Primary Design Invariant

**FS0 SHALL contain only the capabilities necessary to establish a complete remotely operable self-hosting authority loop, and every capability not required for the first successful FS0-governed construction and acceptance of FS1 SHALL be deferred.**

---

# 5. Accepted State and Acceptance Record

FS0 requires one minimal authoritative representation of explicit Governance acceptance and accepted repository state.

Merge state, issue closure, workflow success, or review approval shall not independently answer whether a candidate is accepted.

## Acceptance Record

Each accepted or rejected governed-stage candidate shall have a machine-resolvable acceptance record containing at least:

```text
acceptance identity
Governance stage
governed-work identity
exact candidate identity
disposition
actor attribution
evidence references
decision timestamp
resulting accepted-state relationship where applicable
```

The candidate identity for repository-changing work shall resolve to an exact Git commit SHA.

An acceptance record is Governance state.

It is not a generated interpretation of GitHub merge status.

## Accepted Repository State

FS0 shall maintain one machine-resolvable accepted-state record that identifies:

```text
accepted repository revision
acceptance record authorizing that revision
predecessor accepted revision where applicable
```

For FS0 bootstrap cutover, the first accepted-state record is created by the external bootstrap acceptance process.

After cutover, only FS0 Governance may create a successor accepted-state record.

The accepted-state record is the canonical answer to:

> What exact repository revision is currently accepted?

The default branch HEAD may equal the accepted revision, but equality shall not be the source of acceptance semantics.

---

# 6. FS0 Capability Set

FS0 consists of seven capability groups:

1. Authority Kernel
2. Governance Kernel
3. Normative Requirement Kernel
4. Conformance Kernel
5. Assurance Kernel
6. GitHub Remote Operating Profile
7. Bootstrap Installation and Cutover

These groups are capability boundaries, not necessarily final specification or directory boundaries.

---

# 7. FS0.1 — Authority Kernel

## Purpose

Provide the minimum accepted framework authority necessary to authorize and bound FS0 itself.

## Required Capabilities

FS0 shall establish:

- one authoritative framework namespace under `repo/`;
- one foundational Framework Contract;
- Governance, Conformance, and Assurance as the only authority-bearing keystones;
- explicit delegation from the Framework Contract to each keystone;
- stable machine-resolvable identities for accepted normative authority;
- stable machine-resolvable identities for normative requirements;
- one controlling semantic owner for each independently governed semantic invariant;
- default-deny maintained governed framework state;
- explicitly governed extension points;
- prohibition of implicit authority;
- prohibition of normative authority arising from implementation, validation, review findings, generated artifacts, workflow convention, historical state, or product behavior;
- acyclic normative authority dependency; and
- resolvable provenance for maintained derived framework primitives.

## Minimum Authority Representation

FS0 must be able to resolve at least:

```text
authority identity
requirement identity
authority owner
dependency/delegation relationship
lifecycle state
provenance relationship
```

The representation may be simple.

FS0 does not require the final manifest, schema, or taxonomy design.

## Deferred

FS0 shall defer:

- complete repository artifact taxonomy;
- complete manifest architecture;
- generalized product authority model;
- final extension registry model;
- final generated projection model; and
- final repository structure beyond what FS0 itself requires.

---

# 8. FS0.2 — Governance Kernel

## Purpose

Provide the complete minimum self-building lifecycle.

## Primary Lifecycle

FS0 Governance shall implement:

**Design Proposal**
→ **Design**
→ **Plan**
→ **Build**
→ **accepted repository state**

Design, Plan, and Build shall be distinct governed work.

## Stage Structure

FS0 shall preserve the common three-step stage structure:

| Stage | Analysis | Production | Decision |
| --- | --- | --- | --- |
| Design | Audit | Normalize | Accept |
| Plan | Analyze | Specify | Accept |
| Build | Implement | Verify | Accept |

## Required Governed-Work Properties

Each governed stage shall have:

- stable identity;
- explicit predecessor;
- explicit scope;
- explicit exclusions where material;
- candidate result;
- completion conditions;
- explicit acceptance or rejection;
- provenance; and
- bounded authorization.

## Design

Design shall own persistent normative semantics.

Design shall:

- consume a non-authoritative Design Proposal;
- audit accepted authority and relevant repository state;
- identify conflicts, duplication, missing authority, and unresolved semantics;
- normalize candidate semantics into identified normative requirements;
- identify created, amended, superseded, or withdrawn authority; and
- explicitly accept or reject the normative delta.

Design shall not define implementation detail unless that detail is intentionally normative.

## Plan

Plan shall own realization intent.

Plan shall:

- consume accepted Design authority;
- identify affected artifacts and required work;
- identify required Conformance work;
- identify required Assurance work;
- identify dependencies and sequencing;
- define bounded Build work; and
- explicitly accept or reject realization intent.

Plan shall not create or amend normative semantics.

## Build

Build shall own realization.

Build shall:

- consume the accepted Plan;
- implement only authorized Plan work;
- produce required evidence;
- invoke required Conformance;
- invoke required Assurance;
- verify completion; and
- explicitly accept or reject the resulting repository state.

Build shall not invent Design semantics or Plan intent.

## Required Routing

FS0 shall support:

```text
semantic defect → Design
realization-intent defect → Plan
realization defect → Build
```

## Required Acceptance Rules

Acceptance shall be:

- explicit;
- attributable;
- traceable;
- candidate-specific; and
- separate from merge, issue closure, Conformance success, Assurance findings, or tool declarations.

Governance acceptance shall depend only on authority accepted before the candidate acquires the authority produced by that acceptance.

## Bounded Authorization

A governed work item shall authorize only its explicit scope.

Completion or acceptance shall not independently authorize unrelated or successor work.

---

# 9. FS0.3 — Normative Requirement Kernel

## Purpose

Provide the canonical addressable unit of accepted normative semantics.

## Required Capabilities

Each accepted normative obligation shall have:

- stable requirement identity;
- one controlling normative owner;
- normative statement;
- lifecycle state;
- historical lineage where superseded or withdrawn;
- Conformance applicability; and
- Assurance applicability.

Unidentified accepted normative prose is not sufficient.

## Minimum Quality Discipline

FS0 Design Normalize and Assurance shall be capable of identifying at least:

- materially compound obligations;
- ambiguity;
- contradiction;
- duplication;
- inappropriate implementation leakage; and
- missing semantic ownership.

FS0 does not need the final requirement-quality framework.

---

# 10. FS0.4 — Conformance Kernel

## Purpose

Provide closed mechanical enforcement of accepted normative authority.

## Canonical Relationship

For every accepted normative requirement:

```text
normative requirement
→ canonical Conformance correspondence
→ mechanical | none
```

If applicability is `mechanical`:

```text
normative requirement
→ assertion
→ implementation
→ evidence
→ canonical execution
```

## Required Primitive Classes

FS0 requires only these top-level primitive roles:

1. assertion;
2. support;
3. evidence; and
4. orchestration.

Additional primitive taxonomy is deferred.

## Assertion Identity

Assertion identity shall be distinct from implementation-callable identity.

One requirement may derive multiple assertions.

Multiple assertions may share implementation where identities and provenance remain distinct.

## Required Closure Properties

FS0 Conformance shall establish all four closures.

### Authority Closure

Every maintained Conformance primitive shall resolve to accepted normative authority.

### Coverage Closure

Every mechanically applicable requirement shall resolve to at least one executable assertion.

### Evidence Closure

Every executable assertion shall have the evidence required by FS0 Conformance authority.

### Execution Closure

Every gating assertion shall be reachable from authorized canonical Conformance execution.

## Minimum Evidence

FS0 shall support enough evidence to demonstrate:

- conforming state is accepted;
- targeted violating state is rejected; and
- required assertions actually execute.

The final evidence taxonomy is deferred.

## Canonical Execution

FS0 shall provide one canonical remotely runnable Conformance surface suitable for GitHub Actions.

Local execution may exist as an implementation convenience, but remote canonical execution is required for bootstrap acceptance.

---

# 11. FS0.5 — Assurance Kernel

## Purpose

Provide governed semantic review sufficient to prevent the bootstrap framework from accepting semantically defective authority or realization merely because Conformance passes.

## Canonical Relationship

For every accepted normative requirement:

```text
normative requirement
→ canonical Assurance correspondence
→ required | none
```

If Assurance is required:

```text
accepted authorizing authority
→ review obligation
→ review case
→ review subject + evidence
→ finding
→ Governance disposition
```

## Required Capabilities

FS0 Assurance shall support at least:

- requirement-quality review;
- ambiguity review;
- contradiction review;
- Design fidelity review;
- Plan fidelity review;
- Build realization-fidelity review;
- Conformance interpretation review; and
- evidence-sufficiency review.

## Minimum Finding Vocabulary

FS0 may use a minimal finding vocabulary:

- `satisfied`;
- `defect`;
- `insufficient`; and
- `governance-required`.

The final finding taxonomy is deferred.

## Required Scope Rules

Every governed review case shall identify:

- authorizing authority;
- review obligation;
- reviewed subject;
- evidence;
- exclusions where material; and
- finding identity.

A review subject shall not authorize its own review.

## Required Boundary

Assurance findings are case-specific.

A finding shall not independently create, amend, supersede, or withdraw persistent normative authority.

Persistent semantic change shall route through Governance Design.

---

# 12. FS0.6 — GitHub Remote Operating Profile

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

The exact mapping is a bootstrap implementation decision.

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
| stage acceptance | structured maintained acceptance record attributable to a GitHub actor |
| accepted repository state | structured accepted-state record resolving to exact Git revision |

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

# 13. FS0.7 — Bootstrap Installation and Cutover

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
11. create the bootstrap acceptance record for one exact candidate revision;
12. create the first accepted-state record resolving to that exact revision and acceptance record;
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

# 14. Minimum Installed FS0 State

The exact final tree is not yet fixed.

However, the installed FS0 state must contain enough maintained artifacts to represent:

```text
Framework Contract authority
Governance authority
Conformance authority
Assurance authority
accepted normative requirements
Conformance correspondence
Assurance correspondence
governed work
stage acceptance
Conformance execution
Assurance review cases/findings
GitHub bootstrap operating realization
acceptance records
accepted repository state record
bootstrap cutover record
```

Bootstrap Design shall prefer the smallest representation satisfying those responsibilities.

---

# 15. Explicit FS0 Exclusions

The following are outside FS0 unless later audit proves one is strictly required for the first self-hosted FS1 cycle:

- complete repository structure specification;
- complete artifact taxonomy;
- complete manifest framework;
- product Level 0–3 model;
- permanent functional-set process;
- product decomposition framework;
- rich implementation-plan document model;
- generalized platform profile system;
- support for non-GitHub platforms;
- generalized remote-state administration;
- generated Markdown projections;
- rich schema architecture;
- complete Conformance primitive taxonomy;
- mutation-testing framework;
- advanced evidence classification;
- complete Assurance finding taxonomy;
- reviewer assignment framework;
- product correspondence framework;
- release management;
- migration framework;
- user convenience namespaces; and
- permanent bootstrap tooling.

---

# 16. FS0 Build Principle

Every proposed FS0 artifact shall answer:

> Is this required for FS0 to build and accept FS1 through its own remotely operable Governance, Conformance, and Assurance loop?

If the answer is no, the artifact or capability should be deferred.

---

# 17. FS0 Self-Hosting Demonstration

FS0 is not accepted merely because its own files exist or its bootstrap tests pass.

The decisive proof is construction of a successor functional set.

The initial demonstration target should be a deliberately deferred capability, tentatively:

**FS1 — Repository Structure**

The exact FS1 definition remains outside this proposal.

Artifact classification is intentionally deferred to a later functional set so the first self-hosting proof exercises one bounded semantic domain rather than two coupled domains.

## Required Demonstration

Starting from the accepted FS0 GitHub revision:

### 1. Create FS1 Design Proposal

Create a non-authoritative FS1 proposal through FS0-compatible repository/GitHub state.

### 2. Execute Design

Use FS0 to:

- audit;
- normalize;
- perform required Conformance;
- perform required Assurance; and
- explicitly accept FS1 normative authority.

### 3. Execute Plan

Use FS0 to:

- analyze realization;
- specify bounded work;
- identify Conformance and Assurance changes; and
- explicitly accept the Plan.

### 4. Execute Build

Use FS0 to:

- implement the accepted Plan;
- produce a candidate remote revision;
- execute canonical GitHub Conformance;
- execute required Assurance cases;
- resolve findings; and
- explicitly accept the Build result.

### 5. Publish Accepted State

The accepted FS1 Build result shall become the new accepted repository state on the GitHub remote.

### 6. Begin FS2

Without invoking bootstrap authority, the resulting repository shall be capable of initiating the next Design Proposal and Governance cycle.

---

# 18. FS0 Acceptance Criteria

FS0 bootstrap is complete only when all of the following are true.

## Authority

- FS0 accepted authority is explicitly identifiable.
- All accepted normative requirements have stable identities.
- Semantic ownership is unique.
- Normative authority dependencies are acyclic.
- Maintained governed framework state is positively authorized.
- Derived maintained primitives have resolvable provenance.

## Governance

- Design, Plan, and Build are independently operable.
- Each stage has explicit governed identity and state.
- Acceptance is explicit and candidate-specific.
- Downstream invention is prohibited and testable through audit.
- Authorization is bounded.
- Historical authority lineage is resolvable.

## Conformance

- Every accepted requirement has one canonical Conformance correspondence.
- Every mechanical requirement has executable assertion coverage.
- Every maintained Conformance primitive has provenance.
- Required evidence exists.
- Every gating assertion participates in canonical GitHub execution.

## Assurance

- Every accepted requirement has one canonical Assurance correspondence.
- Required review obligations are identifiable.
- Triggered obligations are instantiated as review cases.
- Findings are attributable, scoped, and evidence-linked.
- Assurance cannot independently create persistent semantics.

## GitHub Operation

- FS0 can be operated without contributor-local filesystem access.
- Candidate revisions are exact and remotely resolvable.
- Canonical Conformance executes remotely.
- Assurance evidence/findings are remotely accessible.
- Explicit acceptance can be resolved independently of merge state.
- Accepted main state is identifiable.
- Unauthorized successor work is distinguishable from authorized work.

## Self-Hosting

- After cutover, FS0 successfully Designs, Plans, Builds, Conforms, Assures, and accepts FS1 through FS0-governed mechanisms.
- FS1 becomes accepted GitHub repository state.
- FS2 can begin without bootstrap authority.

---

# 19. Bootstrap Iteration Strategy

FS0 is expected to require multiple bootstrap iterations.

The intended development loop is:

```text
FS0 Design Proposal
→ generate bootstrap scripts
→ construct fs0-proto
→ initialize Git
→ create/publish GitHub repo
→ audit
→ identify defects
→ revise proposal and/or bootstrap scripts
→ rebuild disposable prototype
→ repeat
```

The prototype repository is disposable until the FS0 end-to-end lifecycle succeeds.

Corrections should prefer fixing the Design Proposal when the defect is semantic and fixing bootstrap scripts when the defect is only realization.

This mirrors the target Governance separation even before FS0 is fully self-hosting.

---

# 20. Bootstrap Completion Boundary

FS0 development ends when the bootstrap process is no longer needed to evolve the framework.

The transition is:

```text
external bootstrap construction
→ accepted FS0
→ self-hosted FS0 Governance
→ FS1 and later functional sets
```

At that point, FS0 becomes the operating kernel from which the remainder of the successor repo-spec is built.

---

# 21. Audit Questions

Before generating bootstrap scripts, this proposal should be audited for:

1. whether every included capability is necessary for the first self-hosted FS1 cycle;
2. whether any omitted capability is actually required to complete that cycle;
3. whether the bootstrap exception is sufficiently bounded;
4. whether GitHub operating requirements accidentally redefine portable Governance semantics;
5. whether explicit acceptance can be represented remotely without equating acceptance with merge;
6. whether the minimum Conformance kernel truly satisfies authority, coverage, evidence, and execution closure;
7. whether the minimum Assurance kernel can perform the semantic reviews needed for Design, Plan, and Build acceptance;
8. whether candidate and accepted repository states are unambiguously identifiable;
9. whether bootstrap artifacts can be retired without breaking provenance;
10. whether FS0 can distinguish accepted authority from candidate authority during its own first self-hosted evolution;
11. whether any current repo-spec mechanism should be reused conceptually to reduce bootstrap risk;
12. whether the proposed FS1 demonstration is sufficiently independent to prove genuine self-hosting; and
13. whether any bootstrap-only shortcut would remain as an undeclared permanent authority path after cutover;
14. whether the acceptance-record and accepted-state-record model is sufficient to distinguish merge from Governance acceptance;
15. whether the fixed FS0 GitHub binding is minimal but complete enough to generate realization scripts without inventing Governance semantics; and
16. whether pre-cutover verification is clearly distinguished from governed FS0 Conformance and Assurance.

