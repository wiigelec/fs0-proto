# FS0 Authority and Governance

## Status

Part of the non-authoritative FS0-Core Bootstrap Design Proposal.

Read `fs0-design.md` first. This chunk does not independently create authority.

---

# Accepted State and Acceptance Record

FS0 requires one minimal authoritative representation of explicit Governance acceptance and accepted repository state.

Merge state, issue closure, workflow success, or review approval shall not independently answer whether a candidate is accepted.

## Acceptance Record

Each accepted or rejected governed-stage candidate shall have one structured machine-resolvable acceptance record attached to the governed-work identity for that stage.

For the FS0 GitHub binding, a governed Design, Plan, or Build acceptance record shall be represented as a structured GitHub issue comment on that stage's governed-work issue.

The record shall contain at least:

```text
record kind
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

The structured comment shall use the Design-defined acceptance-record envelope below. Bootstrap realization shall implement this envelope and shall not invent an alternate acceptance protocol.

## Acceptance Record Envelope

Every machine-readable acceptance comment shall contain exactly one fenced JSON object immediately following the marker:

```text
repo-spec-acceptance:v1
```

The JSON object shall contain at least:

```text
schema_version
record_type
acceptance_id
stage
work_id
candidate_id
disposition
actor
evidence
decision_timestamp
resulting_accepted_state where applicable
```

For governed Design, Plan, and Build acceptance:

```text
schema_version = 1
record_type = governance-acceptance
stage = design | plan | build
```

For bootstrap cutover acceptance:

```text
schema_version = 1
record_type = bootstrap-acceptance
stage = bootstrap
```

`disposition` shall support at least:

```text
accepted
rejected
```

`candidate_id` shall resolve to the exact candidate identity required by the applicable stage and shall be an exact Git commit SHA for repository-changing work.

`evidence` shall be a machine-readable collection of evidence references.

`actor` shall provide attributable actor identity.

`decision_timestamp` shall be an unambiguous timestamp.

`resulting_accepted_state`, when present, shall identify the repository revision that acceptance causes to become eligible for publication through the accepted-state ref.

The marker, field names, and enum values in this envelope are part of FS0 bootstrap Design.

Implementation may choose formatting details that do not change parsing or semantics, but shall not change the marker, required fields, record types, stage values, or disposition values without later accepted Governance.

The candidate identity for repository-changing work shall resolve to an exact Git commit SHA.

The acceptance record exists outside the candidate Git commit and therefore may identify that exact candidate without changing its identity.

An acceptance record is Governance state realized through GitHub.

It is not a generated interpretation of merge status, issue closure, review state, or workflow success.

For initial bootstrap cutover, where no FS0 governed-work issue yet has authority, the external bootstrap process shall create one dedicated GitHub issue for bootstrap provenance and place one structured bootstrap acceptance comment on that issue. The comment shall identify the exact candidate FS0 commit, bootstrap verification evidence, bootstrap semantic-audit evidence, actor attribution, disposition, and decision timestamp.

The bootstrap provenance issue is an external bootstrap record surface only. It shall not be represented as FS0 governed Design, Plan, or Build work.

## Accepted Repository State

FS0 shall realize accepted repository state through one dedicated Git ref named:

```text
refs/heads/accepted
```

The `accepted` ref shall point directly to the exact Git commit currently accepted as repository state.

Moving the `accepted` ref is a realization of an already explicit acceptance decision; moving the ref shall not itself create acceptance.

For a post-cutover Build acceptance:

1. the structured Build acceptance record shall identify the exact candidate commit;
2. the acceptance decision shall be recorded;
3. only after that decision exists may the `accepted` ref advance to that same commit; and
4. the resulting ref shall be verified against the acceptance record.

For bootstrap cutover, the external bootstrap acceptance record shall identify the exact first FS0 candidate commit before the `accepted` ref is created at that commit.

The pair:

```text
structured acceptance record
+
accepted Git ref
```

is the canonical remote representation of accepted repository state.

The canonical answer to:

> What exact repository revision is currently accepted?

is the commit currently referenced by `refs/heads/accepted`, provided that a corresponding valid acceptance record resolves to the same commit.

The default branch HEAD may equal or advance beyond the accepted revision during candidate publication, but default-branch position shall not independently create acceptance.

---

---

# FS0.1 — Authority Kernel

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

---

# FS0.2 — Governance Kernel

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

---

# FS0.3 — Normative Requirement Kernel

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

Each uniquely identified normative requirement shall express exactly one primary normative obligation.

Each normative requirement statement shall contain no more than 300 characters.

Material normative semantics shall not be omitted solely to satisfy the statement-length bound.

Design Normalize shall decompose materially compound obligations into separately identified requirements.

FS0 Design Normalize and Assurance shall be capable of identifying at least:

- materially compound obligations;
- ambiguity;
- contradiction;
- duplication;
- inappropriate implementation leakage; and
- missing semantic ownership.

FS0 does not need the final requirement-quality framework.

---
