---
<!-- DP020-DETAIL-001 -->
doc_id: DP-020
<!-- DP020-DETAIL-002 -->
title: Governance Architecture Proposal
<!-- DP020-DETAIL-003 -->
status: planning-ready
<!-- DP020-DETAIL-004 -->
depends_on:   - DP-010
<!-- DP020-DETAIL-005 -->
artifact_type: design-proposal
<!-- DP020-DETAIL-006 -->
canonical_format: markdown
---

# Governance Architecture Proposal

## Status
<!-- section-id: STATUS -->
<!-- section-id: STATUS -->

<!-- DP020-STATUS-001 -->
Planning-ready Design Proposal.

## Purpose
<!-- section-id: PURPOSE -->
<!-- section-id: PURPOSE -->

<!-- DP020-PURPOSE-001 -->
Define the controlled workflow from iterative Design through Planning and Build to accepted operational repository state.

## Context
<!-- section-id: CONTEXT -->
<!-- section-id: CONTEXT -->

<!-- DP020-CONTEXT-001 -->
Design produces Markdown proposals; Planning selects one functional set and produces a detailed Plan; Build produces operational code.

## Goals
<!-- section-id: GOALS -->
<!-- section-id: GOALS -->

<!-- DP020-GOALS-001 -->
- Preserve the domain architecture and authority boundaries defined by this proposal.
<!-- DP020-GOALS-002 -->
- Make the proposal consumable by incremental functional-set Planning.
<!-- DP020-GOALS-003 -->
- Keep Design statement identity distinct from repository normative identity.

## Non-Goals
<!-- section-id: NON-GOALS -->
<!-- section-id: NON-GOALS -->

<!-- DP020-NON-GOALS-001 -->
- Define one complete implementation plan for the entire proposal.
<!-- DP020-NON-GOALS-002 -->
- Assign repository normative IDs during Design.
<!-- DP020-NON-GOALS-003 -->
- Define file-level pseudo-code in Design unless it is itself a semantic constraint.

## Requirements
<!-- section-id: REQUIREMENTS -->
<!-- section-id: REQUIREMENTS -->

<!-- DP020-REQUIREMENTS-001 -->
The detailed Design below contains addressable Design statements. Statement IDs are non-normative proposal references. `functional-set.json` selects them; `plan.json` owns decomposition and normative distillation.

## Constraints
<!-- section-id: CONSTRAINTS -->
<!-- section-id: CONSTRAINTS -->

<!-- DP020-CONSTRAINTS-001 -->
This proposal remains subordinate to its declared Design dependencies and shall not silently assume authority outside them.

## Architecture
<!-- section-id: ARCHITECTURE -->
<!-- section-id: ARCHITECTURE -->

<!-- DP020-ARCHITECTURE-001 -->
The detailed Design below is semantic input to Planning and may be realized over multiple functional sets.

## Behavior
<!-- section-id: BEHAVIOR -->
<!-- section-id: BEHAVIOR -->

<!-- DP020-BEHAVIOR-001 -->
Planning may consume a bounded subset of this proposal in one functional set; implementation of the entire proposal in one pass is not required.

## Interfaces and Boundaries
<!-- section-id: INTERFACES-AND-BOUNDARIES -->
<!-- section-id: INTERFACES -->

<!-- DP020-INTERFACES-AND-BOUNDARIES-001 -->
Design defines meaning. `functional-set.json` defines selected Design scope. `plan.json` defines normative decomposition and exact implementation intent. Build produces syntactically correct, validated, operational code.

## Invariants
<!-- section-id: INVARIANTS -->
<!-- section-id: INVARIANTS -->

<!-- DP020-INVARIANTS-001 -->
- Design statement IDs remain non-normative.
<!-- DP020-INVARIANTS-002 -->
- Planning owns normative distillation and implementation intent.
<!-- DP020-INVARIANTS-003 -->
- Build shall not invent missing Design semantics or missing Plan intent.

## Alternatives Considered
<!-- section-id: ALTERNATIVES-CONSIDERED -->
<!-- section-id: ALTERNATIVES -->

<!-- DP020-ALTERNATIVES-CONSIDERED-001 -->
Domain-specific alternatives remain in the detailed Design. The revised workflow rejects collapsing Design, Planning, and Build into one artifact or stage.

## Risks and Tradeoffs
<!-- section-id: RISKS-AND-TRADEOFFS -->
<!-- section-id: RISKS -->

<!-- DP020-RISKS-AND-TRADEOFFS-001 -->
Incremental realization may expose missing or ambiguous Design later; those defects must route to Design rather than being silently invented during Planning or Build.

## Open Questions
<!-- section-id: OPEN-QUESTIONS -->
<!-- section-id: OPEN-QUESTIONS -->

<!-- DP020-OPEN-QUESTIONS-001 -->
No blocking workflow-format questions remain. Domain-specific open questions are retained in the detailed Design.

## Acceptance Criteria
<!-- section-id: ACCEPTANCE-CRITERIA -->
<!-- section-id: ACCEPTANCE -->

<!-- DP020-ACCEPTANCE-CRITERIA-001 -->
This proposal is planning-ready when its required sections are complete, its detailed semantics remain coherent with declared dependencies, and its Design statements are addressable.

# Detailed Design

## Framework Contract Basis
<!-- section-id: FRAMEWORK-CONTRACT-BASIS -->

<!-- DP020-FRAMEWORK-CONTRACT-BASIS-001 -->
This proposal assumes the candidate Framework Contract requirements:

<!-- DP020-FRAMEWORK-CONTRACT-BASIS-002 -->
- FC-01 — Framework Authority Location
<!-- DP020-FRAMEWORK-CONTRACT-BASIS-003 -->
- FC-02 — Framework Contract Role
<!-- DP020-FRAMEWORK-CONTRACT-BASIS-004 -->
- FC-03 — Keystone Set
<!-- DP020-FRAMEWORK-CONTRACT-BASIS-005 -->
- FC-04 — Delegated Authority
<!-- DP020-FRAMEWORK-CONTRACT-BASIS-006 -->
- FC-05 — Governance Exclusivity
<!-- DP020-FRAMEWORK-CONTRACT-BASIS-007 -->
- FC-06 — Conformance Exclusivity
<!-- DP020-FRAMEWORK-CONTRACT-BASIS-008 -->
- FC-07 — Assurance Exclusivity
<!-- DP020-FRAMEWORK-CONTRACT-BASIS-009 -->
- FC-08 — Assurance Persistence Boundary
<!-- DP020-FRAMEWORK-CONTRACT-BASIS-010 -->
- FC-09 — Keystone Separation
<!-- DP020-FRAMEWORK-CONTRACT-BASIS-011 -->
- FC-10 — Derived Provenance
<!-- DP020-FRAMEWORK-CONTRACT-BASIS-012 -->
- FC-11 — No Implicit Authority
<!-- DP020-FRAMEWORK-CONTRACT-BASIS-013 -->
- FC-12 — Product Subordination
<!-- DP020-FRAMEWORK-CONTRACT-BASIS-014 -->
- FC-13 — Authority Identity
<!-- DP020-FRAMEWORK-CONTRACT-BASIS-015 -->
- FC-14 — Delegation Resolution

<!-- DP020-FRAMEWORK-CONTRACT-BASIS-016 -->
Governance shall not assume authority beyond that delegated by the Framework Contract.

## Objective
<!-- section-id: OBJECTIVE -->

<!-- DP020-OBJECTIVE-001 -->
Governance shall provide one controlled lifecycle through which detailed non-authoritative design intent becomes accepted repository state.

<!-- DP020-OBJECTIVE-002 -->
The primary Governance lifecycle shall be:

<!-- DP020-OBJECTIVE-003 -->
**Design**  
<!-- DP020-OBJECTIVE-004 -->
→ **Design Proposal**  
<!-- DP020-OBJECTIVE-005 -->
→ **Planning**  
<!-- DP020-OBJECTIVE-006 -->
→ **Plan**  
<!-- DP020-OBJECTIVE-007 -->
→ **Build**

<!-- DP020-OBJECTIVE-008 -->
The Design Proposal is the non-authoritative entry point.

<!-- DP020-OBJECTIVE-009 -->
Design, Plan, and Build are distinct governed stages.

<!-- DP020-OBJECTIVE-010 -->
Their responsibilities are:

<!-- DP020-OBJECTIVE-011 -->
**Design determines intended meaning and behavior and records it in Markdown Design Proposals.**

<!-- DP020-OBJECTIVE-012 -->
**Planning selects one bounded functional set, distills repository normative requirements as needed, and records exact implementation intent in a durable Plan.**

<!-- DP020-OBJECTIVE-013 -->
**Build produces syntactically correct, validated, operational source from the accepted Plan.**

<!-- DP020-OBJECTIVE-014 -->
A downstream stage shall not repair an upstream defect by inventing missing authority.

## Governance Boundary
<!-- section-id: GOVERNANCE-BOUNDARY -->

<!-- DP020-GOVERNANCE-BOUNDARY-001 -->
Governance owns persistent normative change and governed progression between accepted stages.

<!-- DP020-GOVERNANCE-BOUNDARY-002 -->
Governance may:

<!-- DP020-GOVERNANCE-BOUNDARY-003 -->
- receive candidate design intent;
<!-- DP020-GOVERNANCE-BOUNDARY-004 -->
- create or amend accepted normative authority;
<!-- DP020-GOVERNANCE-BOUNDARY-005 -->
- establish accepted realization plans;
<!-- DP020-GOVERNANCE-BOUNDARY-006 -->
- authorize realization work;
<!-- DP020-GOVERNANCE-BOUNDARY-007 -->
- accept governed repository state;
<!-- DP020-GOVERNANCE-BOUNDARY-008 -->
- preserve change lineage;
<!-- DP020-GOVERNANCE-BOUNDARY-009 -->
- supersede or withdraw accepted normative authority;
<!-- DP020-GOVERNANCE-BOUNDARY-010 -->
- consume Conformance findings;
<!-- DP020-GOVERNANCE-BOUNDARY-011 -->
- consume Assurance findings; and
<!-- DP020-GOVERNANCE-BOUNDARY-012 -->
- route defects to the Governance stage responsible for resolving them.

<!-- DP020-GOVERNANCE-BOUNDARY-013 -->
Governance shall not:

<!-- DP020-GOVERNANCE-BOUNDARY-014 -->
- mechanically enforce normative requirements;
<!-- DP020-GOVERNANCE-BOUNDARY-015 -->
- replace Conformance with workflow completion;
<!-- DP020-GOVERNANCE-BOUNDARY-016 -->
- perform semantic review reserved to Assurance;
<!-- DP020-GOVERNANCE-BOUNDARY-017 -->
- treat Assurance findings as persistent normative authority without Governance acceptance;
<!-- DP020-GOVERNANCE-BOUNDARY-018 -->
- infer normative authority from implementation;
<!-- DP020-GOVERNANCE-BOUNDARY-019 -->
- allow Plan to invent missing Design authority;
<!-- DP020-GOVERNANCE-BOUNDARY-020 -->
- allow Build to invent missing Design authority;
<!-- DP020-GOVERNANCE-BOUNDARY-021 -->
- allow Build to invent missing Plan authority; or
<!-- DP020-GOVERNANCE-BOUNDARY-022 -->
- treat a Design Proposal as accepted authority.

## Governance Artifact Model
<!-- section-id: GOVERNANCE-ARTIFACT-MODEL -->

<!-- DP020-GOVERNANCE-ARTIFACT-MODEL-001 -->
Governance shall distinguish four primary artifact classes:

<!-- DP020-GOVERNANCE-ARTIFACT-MODEL-002 -->
1. Design Proposal
<!-- DP020-GOVERNANCE-ARTIFACT-MODEL-003 -->
2. Design governed work
<!-- DP020-GOVERNANCE-ARTIFACT-MODEL-004 -->
3. Plan governed work
<!-- DP020-GOVERNANCE-ARTIFACT-MODEL-005 -->
4. Build governed work

<!-- DP020-GOVERNANCE-ARTIFACT-MODEL-006 -->
Their roles are distinct.

| Artifact | Governance Role |
| --- | --- |
| Design Proposal | detailed non-authoritative candidate design |
| Design governed work | establishes accepted normative change |
| Plan governed work | establishes accepted realization intent |
| Build governed work | realizes accepted realization intent |

<!-- DP020-GOVERNANCE-ARTIFACT-MODEL-007 -->
These artifacts shall participate in one resolvable Governance lineage.

## Design Proposal
<!-- section-id: DESIGN-PROPOSAL -->

<!-- DP020-DESIGN-PROPOSAL-001 -->
A Design Proposal is the entry point into the Governance lifecycle.

<!-- DP020-DESIGN-PROPOSAL-002 -->
A Design Proposal may contain:

<!-- DP020-DESIGN-PROPOSAL-003 -->
- problem definition;
<!-- DP020-DESIGN-PROPOSAL-004 -->
- architectural model;
<!-- DP020-DESIGN-PROPOSAL-005 -->
- candidate invariants;
<!-- DP020-DESIGN-PROPOSAL-006 -->
- candidate normative requirements;
<!-- DP020-DESIGN-PROPOSAL-007 -->
- terminology;
<!-- DP020-DESIGN-PROPOSAL-008 -->
- artifact structures;
<!-- DP020-DESIGN-PROPOSAL-009 -->
- schemas;
<!-- DP020-DESIGN-PROPOSAL-010 -->
- examples;
<!-- DP020-DESIGN-PROPOSAL-011 -->
- implementation consequences;
<!-- DP020-DESIGN-PROPOSAL-012 -->
- migration considerations;
<!-- DP020-DESIGN-PROPOSAL-013 -->
- alternatives;
<!-- DP020-DESIGN-PROPOSAL-014 -->
- conflicts;
<!-- DP020-DESIGN-PROPOSAL-015 -->
- audit questions; and
<!-- DP020-DESIGN-PROPOSAL-016 -->
- unresolved design questions.

<!-- DP020-DESIGN-PROPOSAL-017 -->
Detail does not grant authority.

<!-- DP020-DESIGN-PROPOSAL-018 -->
A Design Proposal remains non-authoritative until candidate semantics are accepted through Design.

<!-- DP020-DESIGN-PROPOSAL-019 -->
A Design Proposal shall not itself:

<!-- DP020-DESIGN-PROPOSAL-020 -->
- create accepted normative authority;
<!-- DP020-DESIGN-PROPOSAL-021 -->
- amend accepted normative authority;
<!-- DP020-DESIGN-PROPOSAL-022 -->
- authorize persistent Conformance behavior;
<!-- DP020-DESIGN-PROPOSAL-023 -->
- authorize realization work;
<!-- DP020-DESIGN-PROPOSAL-024 -->
- supersede accepted authority; or
<!-- DP020-DESIGN-PROPOSAL-025 -->
- become normative merely because governed work references it.

## Primary Governance Stages
<!-- section-id: PRIMARY-GOVERNANCE-STAGES -->

<!-- DP020-PRIMARY-GOVERNANCE-STAGES-001 -->
Governance shall define exactly three primary governed stages:

<!-- DP020-PRIMARY-GOVERNANCE-STAGES-002 -->
1. Design
<!-- DP020-PRIMARY-GOVERNANCE-STAGES-003 -->
2. Plan
<!-- DP020-PRIMARY-GOVERNANCE-STAGES-004 -->
3. Build

<!-- DP020-PRIMARY-GOVERNANCE-STAGES-005 -->
Each stage shall be represented by distinct governed work.

<!-- DP020-PRIMARY-GOVERNANCE-STAGES-006 -->
The Governance lineage is:

<!-- DP020-PRIMARY-GOVERNANCE-STAGES-007 -->
**Design**  
<!-- DP020-PRIMARY-GOVERNANCE-STAGES-008 -->
→ **Design Proposal**  
<!-- DP020-PRIMARY-GOVERNANCE-STAGES-009 -->
→ **Planning**  
<!-- DP020-PRIMARY-GOVERNANCE-STAGES-010 -->
→ **Plan**  
<!-- DP020-PRIMARY-GOVERNANCE-STAGES-011 -->
→ **Build**  
<!-- DP020-PRIMARY-GOVERNANCE-STAGES-012 -->
→ **accepted repository state**

<!-- DP020-PRIMARY-GOVERNANCE-STAGES-013 -->
Each governed stage shall have:

<!-- DP020-PRIMARY-GOVERNANCE-STAGES-014 -->
- a stable identity;
<!-- DP020-PRIMARY-GOVERNANCE-STAGES-015 -->
- an explicit predecessor;
<!-- DP020-PRIMARY-GOVERNANCE-STAGES-016 -->
- a defined responsibility;
<!-- DP020-PRIMARY-GOVERNANCE-STAGES-017 -->
- an explicit candidate result;
<!-- DP020-PRIMARY-GOVERNANCE-STAGES-018 -->
- defined completion conditions;
<!-- DP020-PRIMARY-GOVERNANCE-STAGES-019 -->
- an explicit acceptance decision; and
<!-- DP020-PRIMARY-GOVERNANCE-STAGES-020 -->
- resolvable provenance.

## Stage Authority
<!-- section-id: STAGE-AUTHORITY -->

<!-- DP020-STAGE-AUTHORITY-001 -->
Each stage owns one Governance responsibility.

### Design
<!-- section-id: DESIGN -->

<!-- DP020-DESIGN-001 -->
**What normative authority shall change?**

<!-- DP020-DESIGN-002 -->
Design owns normative semantics.

### Plan
<!-- section-id: PLAN -->

<!-- DP020-PLAN-001 -->
**How shall accepted normative authority be realized?**

<!-- DP020-PLAN-002 -->
Plan owns realization intent.

### Build
<!-- section-id: BUILD -->

<!-- DP020-BUILD-001 -->
**Has accepted realization intent been realized?**

<!-- DP020-BUILD-002 -->
Build owns realization.

<!-- DP020-BUILD-003 -->
A Governance stage shall not independently exercise the responsibility of another stage.

## Stage Structure
<!-- section-id: STAGE-STRUCTURE -->

<!-- DP020-STAGE-STRUCTURE-001 -->
Each primary Governance stage shall contain three substages.

| Stage | Analysis Substage | Production Substage | Decision Substage |
| --- | --- | --- | --- |
| Design | Audit | Normalize | Accept |
| Plan | Analyze | Specify | Accept |
| Build | Implement | Verify | Accept |

<!-- DP020-STAGE-STRUCTURE-002 -->
These substages are part of the proposed Governance architecture rather than illustrative terminology.

<!-- DP020-STAGE-STRUCTURE-003 -->
The shared structural pattern is:

<!-- DP020-STAGE-STRUCTURE-004 -->
1. evaluate authoritative input;
<!-- DP020-STAGE-STRUCTURE-005 -->
2. produce the stage result; and
<!-- DP020-STAGE-STRUCTURE-006 -->
3. explicitly accept or reject that result.

<!-- DP020-STAGE-STRUCTURE-007 -->
The substages have stage-specific semantics and shall not be treated as interchangeable merely because they share a common structure.

## Design
<!-- section-id: DESIGN -->

<!-- DP020-DESIGN-003 -->
Design is the iterative user/AI process that produces and revises Markdown Design Proposals.

<!-- DP020-DESIGN-004 -->
Design may consume:

<!-- DP020-DESIGN-005 -->
- a Design Proposal;
<!-- DP020-DESIGN-006 -->
- accepted normative authority;
<!-- DP020-DESIGN-007 -->
- relevant repository state;
<!-- DP020-DESIGN-008 -->
- Conformance findings;
<!-- DP020-DESIGN-009 -->
- Assurance findings; and
<!-- DP020-DESIGN-010 -->
- governed historical context.

<!-- DP020-DESIGN-011 -->
The durable output of Design is the Design Proposal itself.

<!-- DP020-DESIGN-012 -->
Design shall determine:

<!-- DP020-DESIGN-013 -->
- what normative authority is created;
<!-- DP020-DESIGN-014 -->
- what normative authority is amended;
<!-- DP020-DESIGN-015 -->
- what normative authority is superseded;
<!-- DP020-DESIGN-016 -->
- what normative authority is withdrawn;
<!-- DP020-DESIGN-017 -->
- what existing authority remains unchanged; and
<!-- DP020-DESIGN-018 -->
- what candidate semantics remain unaccepted.

<!-- DP020-DESIGN-019 -->
Design shall not define realization details unless those details are intentionally normative.

## Design Audit
<!-- section-id: DESIGN-AUDIT -->

<!-- DP020-DESIGN-AUDIT-001 -->
Design Audit compares candidate design intent against accepted authority and relevant repository state.

<!-- DP020-DESIGN-AUDIT-002 -->
Audit should identify:

<!-- DP020-DESIGN-AUDIT-003 -->
- existing authority relevant to the proposal;
<!-- DP020-DESIGN-AUDIT-004 -->
- conflicting authority;
<!-- DP020-DESIGN-AUDIT-005 -->
- duplicated authority;
<!-- DP020-DESIGN-AUDIT-006 -->
- missing authority;
<!-- DP020-DESIGN-AUDIT-007 -->
- implementation behavior with no normative owner;
<!-- DP020-DESIGN-AUDIT-008 -->
- candidate semantics already expressed elsewhere;
<!-- DP020-DESIGN-AUDIT-009 -->
- historical or bootstrap behavior that should not become target semantics;
<!-- DP020-DESIGN-AUDIT-010 -->
- cross-keystone responsibility violations; and
<!-- DP020-DESIGN-AUDIT-011 -->
- unresolved semantic questions.

<!-- DP020-DESIGN-AUDIT-012 -->
Audit produces findings.

<!-- DP020-DESIGN-AUDIT-013 -->
Audit findings are not accepted normative authority.

## Design Normalize
<!-- section-id: DESIGN-NORMALIZE -->

<!-- DP020-DESIGN-NORMALIZE-001 -->
Repository normative decomposition and identity assignment belong to Planning, not Design.

<!-- DP020-DESIGN-NORMALIZE-002 -->
Normalization should:

<!-- DP020-DESIGN-NORMALIZE-003 -->
- assign or preserve stable identities;
<!-- DP020-DESIGN-NORMALIZE-004 -->
- separate independent obligations;
<!-- DP020-DESIGN-NORMALIZE-005 -->
- remove duplication;
<!-- DP020-DESIGN-NORMALIZE-006 -->
- distinguish normative semantics from rationale;
<!-- DP020-DESIGN-NORMALIZE-007 -->
- distinguish normative semantics from examples;
<!-- DP020-DESIGN-NORMALIZE-008 -->
- distinguish normative semantics from implementation guidance;
<!-- DP020-DESIGN-NORMALIZE-009 -->
- identify supersession relationships; and
<!-- DP020-DESIGN-NORMALIZE-010 -->
- preserve intended semantic meaning.

<!-- DP020-DESIGN-NORMALIZE-011 -->
Detailed requirement-quality criteria may be established by subordinate Governance, Conformance, or Assurance authority according to their respective responsibilities.

<!-- DP020-DESIGN-NORMALIZE-012 -->
Normalization shall not alter intended semantics merely to simplify implementation or mechanical enforcement.

## Design Accept
<!-- section-id: DESIGN-ACCEPT -->

<!-- DP020-DESIGN-ACCEPT-001 -->
Design Accept decides whether the proposed normative delta becomes accepted normative authority.

<!-- DP020-DESIGN-ACCEPT-002 -->
The accepted Design result shall identify:

<!-- DP020-DESIGN-ACCEPT-003 -->
- normative authority created;
<!-- DP020-DESIGN-ACCEPT-004 -->
- normative authority amended;
<!-- DP020-DESIGN-ACCEPT-005 -->
- normative authority superseded;
<!-- DP020-DESIGN-ACCEPT-006 -->
- normative authority withdrawn; and
<!-- DP020-DESIGN-ACCEPT-007 -->
- candidate semantics explicitly left unaccepted.

<!-- DP020-DESIGN-ACCEPT-008 -->
Only an accepted Design result may establish persistent normative change.

<!-- DP020-DESIGN-ACCEPT-009 -->
An accepted Design result authorizes Plan.

## Design Output
<!-- section-id: DESIGN-OUTPUT -->

<!-- DP020-DESIGN-OUTPUT-001 -->
The durable output of Design is the exact planning-ready Markdown Design Proposal revision consumed by Planning.

<!-- DP020-DESIGN-OUTPUT-002 -->
The Design Proposal remains non-authoritative provenance and context.

<!-- DP020-DESIGN-OUTPUT-003 -->
The Design governed-work artifact remains Governance evidence.

<!-- DP020-DESIGN-OUTPUT-004 -->
Neither replaces accepted normative authority.

## Plan
<!-- section-id: PLAN -->

<!-- DP020-PLAN-003 -->
Planning audits planning-ready Design against accepted implementation, selects one bounded functional set, and produces a durable Plan for that functional set.

<!-- DP020-PLAN-004 -->
Plan answers:

<!-- DP020-PLAN-005 -->
**How shall the accepted Design be realized without changing its normative semantics?**

<!-- DP020-PLAN-006 -->
Plan may identify:

<!-- DP020-PLAN-007 -->
- affected artifacts;
<!-- DP020-PLAN-008 -->
- realization work;
<!-- DP020-PLAN-009 -->
- dependency ordering;
<!-- DP020-PLAN-010 -->
- schema changes;
<!-- DP020-PLAN-011 -->
- generated artifacts;
<!-- DP020-PLAN-012 -->
- Conformance work;
<!-- DP020-PLAN-013 -->
- Assurance work;
<!-- DP020-PLAN-014 -->
- cleanup work;
<!-- DP020-PLAN-015 -->
- migration work; and
<!-- DP020-PLAN-016 -->
- expected completion evidence.

<!-- DP020-PLAN-017 -->
Plan shall not create or amend normative semantics.

<!-- DP020-PLAN-018 -->
If planning requires semantic change, work shall return to Design.

## Plan Analyze
<!-- section-id: PLAN-ANALYZE -->

<!-- DP020-PLAN-ANALYZE-001 -->
Plan Analyze determines the realization impact of accepted Design authority.

<!-- DP020-PLAN-ANALYZE-002 -->
Analysis should identify:

<!-- DP020-PLAN-ANALYZE-003 -->
- affected normative authority;
<!-- DP020-PLAN-ANALYZE-004 -->
- affected implementation;
<!-- DP020-PLAN-ANALYZE-005 -->
- affected derived artifacts;
<!-- DP020-PLAN-ANALYZE-006 -->
- affected Conformance mechanisms;
<!-- DP020-PLAN-ANALYZE-007 -->
- required Assurance work;
<!-- DP020-PLAN-ANALYZE-008 -->
- dependencies;
<!-- DP020-PLAN-ANALYZE-009 -->
- sequencing constraints;
<!-- DP020-PLAN-ANALYZE-010 -->
- obsolete artifacts; and
<!-- DP020-PLAN-ANALYZE-011 -->
- realization risks.

<!-- DP020-PLAN-ANALYZE-012 -->
Plan analysis shall remain traceable to accepted Design authority.

## Plan Specify
<!-- section-id: PLAN-SPECIFY -->

<!-- DP020-PLAN-SPECIFY-001 -->
Plan Specify converts impact analysis into candidate realization intent.

<!-- DP020-PLAN-SPECIFY-002 -->
The candidate Plan should identify:

<!-- DP020-PLAN-SPECIFY-003 -->
- governed work items;
<!-- DP020-PLAN-SPECIFY-004 -->
- affected artifact classes or paths where known;
<!-- DP020-PLAN-SPECIFY-005 -->
- dependencies;
<!-- DP020-PLAN-SPECIFY-006 -->
- sequencing;
<!-- DP020-PLAN-SPECIFY-007 -->
- required Conformance changes;
<!-- DP020-PLAN-SPECIFY-008 -->
- required Assurance checkpoints;
<!-- DP020-PLAN-SPECIFY-009 -->
- removals;
<!-- DP020-PLAN-SPECIFY-010 -->
- generated changes; and
<!-- DP020-PLAN-SPECIFY-011 -->
- expected completion evidence.

<!-- DP020-PLAN-SPECIFY-012 -->
Every governed Plan work item shall resolve to accepted normative authority that requires or authorizes the work.

<!-- DP020-PLAN-SPECIFY-013 -->
A Plan shall not contain orphan governed work.

## Plan Accept
<!-- section-id: PLAN-ACCEPT -->

<!-- DP020-PLAN-ACCEPT-001 -->
Plan Accept decides whether candidate realization intent becomes the accepted Plan.

<!-- DP020-PLAN-ACCEPT-002 -->
Plan acceptance shall establish that:

<!-- DP020-PLAN-ACCEPT-003 -->
- accepted Design obligations requiring realization are addressed;
<!-- DP020-PLAN-ACCEPT-004 -->
- the Plan does not introduce unauthorized semantics;
<!-- DP020-PLAN-ACCEPT-005 -->
- dependencies are coherent;
<!-- DP020-PLAN-ACCEPT-006 -->
- required Conformance work is identified;
<!-- DP020-PLAN-ACCEPT-007 -->
- required Assurance work is identified; and
<!-- DP020-PLAN-ACCEPT-008 -->
- Build can proceed without unresolved Design decisions.

<!-- DP020-PLAN-ACCEPT-009 -->
An accepted Plan authorizes Build.

## Plan Output
<!-- section-id: PLAN-OUTPUT -->

<!-- DP020-PLAN-OUTPUT-001 -->
The durable output of Planning is the accepted Plan artifact for one functional set.

<!-- DP020-PLAN-OUTPUT-002 -->
The accepted Plan does not become normative framework or product semantics.

<!-- DP020-PLAN-OUTPUT-003 -->
It remains subordinate to accepted Design authority.

## Build
<!-- section-id: BUILD -->

<!-- DP020-BUILD-004 -->
Build realizes the accepted Plan as syntactically correct, validated, operational source.

<!-- DP020-BUILD-005 -->
Build answers:

<!-- DP020-BUILD-006 -->
**Has accepted realization intent been implemented into repository state?**

<!-- DP020-BUILD-007 -->
Build may:

<!-- DP020-BUILD-008 -->
- modify implementation;
<!-- DP020-BUILD-009 -->
- create or modify derived artifacts;
<!-- DP020-BUILD-010 -->
- create or modify Conformance mechanisms where authorized;
<!-- DP020-BUILD-011 -->
- produce Assurance evidence;
<!-- DP020-BUILD-012 -->
- remove superseded implementation; and
<!-- DP020-BUILD-013 -->
- regenerate governed outputs.

<!-- DP020-BUILD-014 -->
Build shall not:

<!-- DP020-BUILD-015 -->
- create normative requirements;
<!-- DP020-BUILD-016 -->
- reinterpret accepted Design;
<!-- DP020-BUILD-017 -->
- expand realization scope without Governance authority;
<!-- DP020-BUILD-018 -->
- omit required Plan work;
<!-- DP020-BUILD-019 -->
- invent mechanical enforcement without accepted normative authority; or
<!-- DP020-BUILD-020 -->
- convert implementation convenience into authority.

## Build Implement
<!-- section-id: BUILD-IMPLEMENT -->

<!-- DP020-BUILD-IMPLEMENT-001 -->
Build Implement performs accepted realization work.

<!-- DP020-BUILD-IMPLEMENT-002 -->
Each governed Build change shall resolve to an accepted Plan work item that authorizes the change.

<!-- DP020-BUILD-IMPLEMENT-003 -->
Implementation may expose upstream defects but shall not silently repair them by creating missing authority.

## Build Verify
<!-- section-id: BUILD-VERIFY -->

<!-- DP020-BUILD-VERIFY-001 -->
Build Verify evaluates the candidate realization against the accepted Plan and applicable accepted authority.

<!-- DP020-BUILD-VERIFY-002 -->
Verification may consume:

<!-- DP020-BUILD-VERIFY-003 -->
- Conformance results;
<!-- DP020-BUILD-VERIFY-004 -->
- Assurance findings;
<!-- DP020-BUILD-VERIFY-005 -->
- generated-output checks;
<!-- DP020-BUILD-VERIFY-006 -->
- provenance checks;
<!-- DP020-BUILD-VERIFY-007 -->
- Plan-completion evidence; and
<!-- DP020-BUILD-VERIFY-008 -->
- repository-state inspection.

<!-- DP020-BUILD-VERIFY-009 -->
Build Verify does not replace Conformance or Assurance.

<!-- DP020-BUILD-VERIFY-010 -->
It consumes their governed outputs where required.

## Build Accept
<!-- section-id: BUILD-ACCEPT -->

<!-- DP020-BUILD-ACCEPT-001 -->
Build Accept decides whether the candidate realization becomes accepted repository state.

<!-- DP020-BUILD-ACCEPT-002 -->
Build acceptance shall require:

<!-- DP020-BUILD-ACCEPT-003 -->
- accepted Plan work is complete;
<!-- DP020-BUILD-ACCEPT-004 -->
- applicable Conformance obligations are satisfied;
<!-- DP020-BUILD-ACCEPT-005 -->
- required Assurance findings are resolved or dispositioned;
<!-- DP020-BUILD-ACCEPT-006 -->
- required generated artifacts are current;
<!-- DP020-BUILD-ACCEPT-007 -->
- required provenance is complete; and
<!-- DP020-BUILD-ACCEPT-008 -->
- no unresolved upstream defect is hidden in Build.

<!-- DP020-BUILD-ACCEPT-009 -->
Build acceptance establishes the accepted repository state produced by the Governance lifecycle.

<!-- DP020-BUILD-ACCEPT-010 -->
Build acceptance shall not create normative semantics beyond accepted Design authority.

## Stage Acceptance
<!-- section-id: STAGE-ACCEPTANCE -->

<!-- DP020-STAGE-ACCEPTANCE-001 -->
Acceptance is the common Governance decision that promotes a candidate stage result into the accepted result of that stage.

<!-- DP020-STAGE-ACCEPTANCE-002 -->
Acceptance shall be:

<!-- DP020-STAGE-ACCEPTANCE-003 -->
- explicit;
<!-- DP020-STAGE-ACCEPTANCE-004 -->
- attributable;
<!-- DP020-STAGE-ACCEPTANCE-005 -->
- traceable; and
<!-- DP020-STAGE-ACCEPTANCE-006 -->
- distinguishable from incidental repository or platform activity.

<!-- DP020-STAGE-ACCEPTANCE-007 -->
Acceptance shall not arise solely because:

<!-- DP020-STAGE-ACCEPTANCE-008 -->
- code was merged;
<!-- DP020-STAGE-ACCEPTANCE-009 -->
- an issue was closed;
<!-- DP020-STAGE-ACCEPTANCE-010 -->
- Conformance passed;
<!-- DP020-STAGE-ACCEPTANCE-011 -->
- review approval was recorded;
<!-- DP020-STAGE-ACCEPTANCE-012 -->
- an AI agent declared completion; or
<!-- DP020-STAGE-ACCEPTANCE-013 -->
- downstream activity began.

<!-- DP020-STAGE-ACCEPTANCE-014 -->
Conformance or Assurance evidence may be required for acceptance without themselves constituting Governance acceptance.

<!-- DP020-STAGE-ACCEPTANCE-015 -->
The consequence of acceptance depends on the stage:

| Stage | Acceptance Consequence |
| --- | --- |
| Design | candidate normative delta becomes accepted normative authority |
| Plan | candidate realization intent becomes the accepted Plan and authorizes Build |
| Build | candidate realization becomes accepted repository state |

## Stage Rejection
<!-- section-id: STAGE-REJECTION -->

<!-- DP020-STAGE-REJECTION-001 -->
A Governance stage may reject its candidate result.

<!-- DP020-STAGE-REJECTION-002 -->
Rejection shall preserve:

<!-- DP020-STAGE-REJECTION-003 -->
- the rejected candidate;
<!-- DP020-STAGE-REJECTION-004 -->
- the reason for rejection; and
<!-- DP020-STAGE-REJECTION-005 -->
- provenance to the governed work.

<!-- DP020-STAGE-REJECTION-006 -->
Rejected semantics, realization intent, or realization shall not become accepted merely because downstream artifacts or implementation exist.

## Feedback Routing
<!-- section-id: FEEDBACK-ROUTING -->

<!-- DP020-FEEDBACK-ROUTING-001 -->
Governance shall route defects to the stage responsible for the defective responsibility.

### Design Routing
<!-- section-id: DESIGN-ROUTING -->

<!-- DP020-DESIGN-ROUTING-001 -->
Work shall return to Design when:

<!-- DP020-DESIGN-ROUTING-002 -->
- accepted normative authority is ambiguous;
<!-- DP020-DESIGN-ROUTING-003 -->
- accepted normative authority is contradictory;
<!-- DP020-DESIGN-ROUTING-004 -->
- required semantics are missing;
<!-- DP020-DESIGN-ROUTING-005 -->
- a new semantic choice is required; or
<!-- DP020-DESIGN-ROUTING-006 -->
- accepted semantics require amendment.

### Plan Routing
<!-- section-id: PLAN-ROUTING -->

<!-- DP020-PLAN-ROUTING-001 -->
Work shall return to Plan when:

<!-- DP020-PLAN-ROUTING-002 -->
- realization work is missing;
<!-- DP020-PLAN-ROUTING-003 -->
- dependency analysis is incomplete;
<!-- DP020-PLAN-ROUTING-004 -->
- sequencing is incorrect;
<!-- DP020-PLAN-ROUTING-005 -->
- realization strategy must change; and
<!-- DP020-PLAN-ROUTING-006 -->
- accepted normative semantics do not need to change.

### Build Routing
<!-- section-id: BUILD-ROUTING -->

<!-- DP020-BUILD-ROUTING-001 -->
Work shall remain in Build when:

<!-- DP020-BUILD-ROUTING-002 -->
- implementation is incorrect;
<!-- DP020-BUILD-ROUTING-003 -->
- accepted Plan work is incomplete;
<!-- DP020-BUILD-ROUTING-004 -->
- generated artifacts are stale;
<!-- DP020-BUILD-ROUTING-005 -->
- implementation cleanup remains;
<!-- DP020-BUILD-ROUTING-006 -->
- required evidence has not been produced; and
<!-- DP020-BUILD-ROUTING-007 -->
- neither Design nor Plan must change.

<!-- DP020-BUILD-ROUTING-008 -->
The governing routing rule is:

<!-- DP020-BUILD-ROUTING-009 -->
**Semantic defect → Design**

<!-- DP020-BUILD-ROUTING-010 -->
**Realization-intent defect → Plan**

<!-- DP020-BUILD-ROUTING-011 -->
**Realization defect → Build**

## No Downstream Invention
<!-- section-id: NO-DOWNSTREAM-INVENTION -->

<!-- DP020-NO-DOWNSTREAM-INVENTION-001 -->
A downstream Governance stage shall not create authority required from an upstream stage.

<!-- DP020-NO-DOWNSTREAM-INVENTION-002 -->
Plan shall not create normative semantics missing from Design.

<!-- DP020-NO-DOWNSTREAM-INVENTION-003 -->
Build shall not create normative semantics missing from Design.

<!-- DP020-NO-DOWNSTREAM-INVENTION-004 -->
Build shall not create realization intent missing from Plan.

<!-- DP020-NO-DOWNSTREAM-INVENTION-005 -->
Downstream discovery of an upstream defect shall cause backward routing rather than local invention.

## Governance Provenance
<!-- section-id: GOVERNANCE-PROVENANCE -->

<!-- DP020-GOVERNANCE-PROVENANCE-001 -->
A completed Governance lifecycle shall preserve a resolvable lineage:

<!-- DP020-GOVERNANCE-PROVENANCE-002 -->
**Design Proposal**  
<!-- DP020-GOVERNANCE-PROVENANCE-003 -->
→ **Design governed work**  
<!-- DP020-GOVERNANCE-PROVENANCE-004 -->
→ **accepted normative delta**  
<!-- DP020-GOVERNANCE-PROVENANCE-005 -->
→ **Plan governed work**  
<!-- DP020-GOVERNANCE-PROVENANCE-006 -->
→ **accepted realization intent**  
<!-- DP020-GOVERNANCE-PROVENANCE-007 -->
→ **Build governed work**  
<!-- DP020-GOVERNANCE-PROVENANCE-008 -->
→ **accepted repository state**

<!-- DP020-GOVERNANCE-PROVENANCE-009 -->
The lineage shall make it possible to determine:

<!-- DP020-GOVERNANCE-PROVENANCE-010 -->
- why a change exists;
<!-- DP020-GOVERNANCE-PROVENANCE-011 -->
- what proposal initiated it;
<!-- DP020-GOVERNANCE-PROVENANCE-012 -->
- what normative authority changed;
<!-- DP020-GOVERNANCE-PROVENANCE-013 -->
- what accepted Plan authorized realization;
<!-- DP020-GOVERNANCE-PROVENANCE-014 -->
- what Build realized that Plan; and
<!-- DP020-GOVERNANCE-PROVENANCE-015 -->
- what Conformance and Assurance evidence supported acceptance.

## Governed Work Provenance
<!-- section-id: GOVERNED-WORK-PROVENANCE -->

<!-- DP020-GOVERNED-WORK-PROVENANCE-001 -->
Governed work shall not exist without resolvable authority.

<!-- DP020-GOVERNED-WORK-PROVENANCE-002 -->
Each governed Plan work item shall resolve to accepted normative authority that requires or authorizes it.

<!-- DP020-GOVERNED-WORK-PROVENANCE-003 -->
Each governed Build change shall resolve to an accepted Plan work item that authorizes the change.

<!-- DP020-GOVERNED-WORK-PROVENANCE-004 -->
The exact provenance representation belongs in detailed Governance authority.

## Normative Requirement Identity
<!-- section-id: NORMATIVE-REQUIREMENT-IDENTITY -->

<!-- DP020-NORMATIVE-REQUIREMENT-IDENTITY-001 -->
Accepted normative obligations shall be represented by stable machine-resolvable normative requirement identities.

<!-- DP020-NORMATIVE-REQUIREMENT-IDENTITY-002 -->
The normative requirement is the canonical addressable unit of accepted normative semantics.

<!-- DP020-NORMATIVE-REQUIREMENT-IDENTITY-003 -->
A normative obligation shall not remain accepted only as unidentified prose that escapes Conformance and Assurance correspondence.

## Governed Identity
<!-- section-id: GOVERNED-IDENTITY -->

<!-- DP020-GOVERNED-IDENTITY-001 -->
Governance artifacts participating in authoritative lineage shall have stable identities.

<!-- DP020-GOVERNED-IDENTITY-002 -->
At minimum, identity shall exist for:

<!-- DP020-GOVERNED-IDENTITY-003 -->
- Design Proposal;
<!-- DP020-GOVERNED-IDENTITY-004 -->
- Design governed work;
<!-- DP020-GOVERNED-IDENTITY-005 -->
- accepted Design result;
<!-- DP020-GOVERNED-IDENTITY-006 -->
- Plan governed work;
<!-- DP020-GOVERNED-IDENTITY-007 -->
- accepted Plan result;
<!-- DP020-GOVERNED-IDENTITY-008 -->
- Build governed work; and
<!-- DP020-GOVERNED-IDENTITY-009 -->
- accepted Build result.

<!-- DP020-GOVERNED-IDENTITY-010 -->
The exact identity representation belongs in detailed Governance authority.

## Evaluation Disposition
<!-- section-id: EVALUATION-DISPOSITION -->

<!-- DP020-EVALUATION-DISPOSITION-001 -->
Each accepted normative requirement shall have governed Conformance and Assurance applicability.

<!-- DP020-EVALUATION-DISPOSITION-002 -->
A requirement for which Conformance applicability is `none` and Assurance applicability is `none` shall have a governed rationale explaining why neither keystone directly evaluates that requirement.

<!-- DP020-EVALUATION-DISPOSITION-003 -->
Governance owns acceptance of this cross-keystone disposition.

<!-- DP020-EVALUATION-DISPOSITION-004 -->
Neither Conformance nor Assurance shall independently determine the responsibility of the other keystone.

## Acceptance Authority
<!-- section-id: ACCEPTANCE-AUTHORITY -->

<!-- DP020-ACCEPTANCE-AUTHORITY-001 -->
Governance acceptance shall depend only on authority accepted before the candidate result acquires the authority produced by that acceptance.

<!-- DP020-ACCEPTANCE-AUTHORITY-002 -->
A candidate authority shall not require itself, or authority that exists only because that candidate has already been accepted, as a prerequisite for its own acceptance.

<!-- DP020-ACCEPTANCE-AUTHORITY-003 -->
This prevents circular self-authorization during framework evolution and self-hosting.

## Governed State
<!-- section-id: GOVERNED-STATE -->

<!-- DP020-GOVERNED-STATE-001 -->
Governance state shall be explicitly represented.

<!-- DP020-GOVERNED-STATE-002 -->
Governed authorization shall be bounded to explicitly governed scope.

<!-- DP020-GOVERNED-STATE-003 -->
A governed work item shall not independently authorize unrelated or successor work merely because the current work is accepted or complete.

<!-- DP020-GOVERNED-STATE-004 -->
A governed-work artifact shall not rely solely on surrounding platform state to determine its Governance state.

<!-- DP020-GOVERNED-STATE-005 -->
Detailed state vocabulary and transition rules belong in subordinate Governance authority.

## Authority Lifecycle
<!-- section-id: AUTHORITY-LIFECYCLE -->

<!-- DP020-AUTHORITY-LIFECYCLE-001 -->
Governance shall support persistent normative-authority lifecycle operations including:

<!-- DP020-AUTHORITY-LIFECYCLE-002 -->
- creation;
<!-- DP020-AUTHORITY-LIFECYCLE-003 -->
- amendment;
<!-- DP020-AUTHORITY-LIFECYCLE-004 -->
- supersession; and
<!-- DP020-AUTHORITY-LIFECYCLE-005 -->
- withdrawal.

<!-- DP020-AUTHORITY-LIFECYCLE-006 -->
Superseded or withdrawn normative authority shall remain historically resolvable.

<!-- DP020-AUTHORITY-LIFECYCLE-007 -->
A normative identity shall not be reused in a manner that obscures previously accepted authority.

<!-- DP020-AUTHORITY-LIFECYCLE-008 -->
Authority lifecycle operations shall preserve lineage to the Governance work that authorized them.

## Relationship to Conformance
<!-- section-id: RELATIONSHIP-TO-CONFORMANCE -->

<!-- DP020-RELATIONSHIP-TO-CONFORMANCE-001 -->
Governance may require Conformance evidence for stage acceptance.

<!-- DP020-RELATIONSHIP-TO-CONFORMANCE-002 -->
Governance shall not define mechanical enforcement semantics merely because it requires such evidence.

<!-- DP020-RELATIONSHIP-TO-CONFORMANCE-003 -->
Conformance remains responsible for mechanically evaluating observable state against accepted normative authority.

<!-- DP020-RELATIONSHIP-TO-CONFORMANCE-004 -->
Passing Conformance does not create normative authority or constitute Governance acceptance.

## Relationship to Assurance
<!-- section-id: RELATIONSHIP-TO-ASSURANCE -->

<!-- DP020-RELATIONSHIP-TO-ASSURANCE-001 -->
Governance may require Assurance findings for stage acceptance.

<!-- DP020-RELATIONSHIP-TO-ASSURANCE-002 -->
Assurance may identify:

<!-- DP020-RELATIONSHIP-TO-ASSURANCE-003 -->
- ambiguity;
<!-- DP020-RELATIONSHIP-TO-ASSURANCE-004 -->
- contradiction;
<!-- DP020-RELATIONSHIP-TO-ASSURANCE-005 -->
- semantic insufficiency;
<!-- DP020-RELATIONSHIP-TO-ASSURANCE-006 -->
- evidence insufficiency; and
<!-- DP020-RELATIONSHIP-TO-ASSURANCE-007 -->
- case-specific semantic conclusions.

<!-- DP020-RELATIONSHIP-TO-ASSURANCE-008 -->
Governance remains responsible for persistent normative change.

<!-- DP020-RELATIONSHIP-TO-ASSURANCE-009 -->
An Assurance finding requiring persistent semantic change shall route to Design.

<!-- DP020-RELATIONSHIP-TO-ASSURANCE-010 -->
An Assurance finding does not itself constitute Governance acceptance.

## Human and Automated Actors
<!-- section-id: HUMAN-AND-AUTOMATED-ACTORS -->

<!-- DP020-HUMAN-AND-AUTOMATED-ACTORS-001 -->
Governance may be performed by humans, automated tooling, AI agents, or combinations of them where authorized.

<!-- DP020-HUMAN-AND-AUTOMATED-ACTORS-002 -->
Actor capability does not determine authority.

<!-- DP020-HUMAN-AND-AUTOMATED-ACTORS-003 -->
Authority derives from accepted Governance rules.

<!-- DP020-HUMAN-AND-AUTOMATED-ACTORS-004 -->
The ability to inspect, modify, merge, close, approve, or otherwise manipulate repository or platform state does not independently grant Governance authority.

## Candidate Governance Requirements
<!-- section-id: CANDIDATE-GOVERNANCE-REQUIREMENTS -->

<!-- DP020-CANDIDATE-GOVERNANCE-REQUIREMENTS-001 -->
The following proposal-local statements are Design input. Their labels are non-normative; Planning may distill repository normative requirements from any combination of selected Design statements.

### GOV-01 — Governance Lifecycle
<!-- section-id: GOV-01-GOVERNANCE-LIFECYCLE -->

<!-- DP020-GOV-01-GOVERNANCE-LIFECYCLE-001 -->
**Governance SHALL define Design, Plan, and Build as its three primary governed stages.**

### GOV-02 — Design Proposal Entry
<!-- section-id: GOV-02-DESIGN-PROPOSAL-ENTRY -->

<!-- DP020-GOV-02-DESIGN-PROPOSAL-ENTRY-001 -->
**A Governance lifecycle SHALL originate from a non-authoritative Design Proposal.**

### GOV-03 — Distinct Governed Work
<!-- section-id: GOV-03-DISTINCT-GOVERNED-WORK -->

<!-- DP020-GOV-03-DISTINCT-GOVERNED-WORK-001 -->
**Design, Plan, and Build SHALL each be represented by distinct governed work.**

### GOV-04 — Stage Lineage
<!-- section-id: GOV-04-STAGE-LINEAGE -->

<!-- DP020-GOV-04-STAGE-LINEAGE-001 -->
**Each governed stage SHALL resolve to the predecessor artifact or accepted result that authorizes it.**

### GOV-05 — Design Authority
<!-- section-id: GOV-05-DESIGN-AUTHORITY -->

<!-- DP020-GOV-05-DESIGN-AUTHORITY-001 -->
**Design SHALL be the Governance stage responsible for creating or changing accepted normative authority.**

### GOV-06 — Plan Authority
<!-- section-id: GOV-06-PLAN-AUTHORITY -->

<!-- DP020-GOV-06-PLAN-AUTHORITY-001 -->
**Plan SHALL be the Governance stage responsible for establishing realization intent for accepted Design authority.**

### GOV-07 — Plan Semantic Boundary
<!-- section-id: GOV-07-PLAN-SEMANTIC-BOUNDARY -->

<!-- DP020-GOV-07-PLAN-SEMANTIC-BOUNDARY-001 -->
**Plan SHALL NOT independently create or amend normative semantics.**

### GOV-08 — Build Authority
<!-- section-id: GOV-08-BUILD-AUTHORITY -->

<!-- DP020-GOV-08-BUILD-AUTHORITY-001 -->
**Build SHALL be the Governance stage responsible for realizing the accepted Plan.**

### GOV-09 — Build Semantic Boundary
<!-- section-id: GOV-09-BUILD-SEMANTIC-BOUNDARY -->

<!-- DP020-GOV-09-BUILD-SEMANTIC-BOUNDARY-001 -->
**Build SHALL NOT independently create or amend normative semantics.**

### GOV-10 — Stage Separation
<!-- section-id: GOV-10-STAGE-SEPARATION -->

<!-- DP020-GOV-10-STAGE-SEPARATION-001 -->
**A Governance stage SHALL NOT independently exercise authority assigned to another Governance stage.**

### GOV-11 — Explicit Stage Acceptance
<!-- section-id: GOV-11-EXPLICIT-STAGE-ACCEPTANCE -->

<!-- DP020-GOV-11-EXPLICIT-STAGE-ACCEPTANCE-001 -->
**A governed stage result SHALL NOT become accepted until explicitly accepted through Governance.**

### GOV-12 — Acceptance Independence
<!-- section-id: GOV-12-ACCEPTANCE-INDEPENDENCE -->

<!-- DP020-GOV-12-ACCEPTANCE-INDEPENDENCE-001 -->
**Governance acceptance SHALL NOT arise solely from incidental repository or platform activity.**

### GOV-13 — Acceptance Consequence
<!-- section-id: GOV-13-ACCEPTANCE-CONSEQUENCE -->

<!-- DP020-GOV-13-ACCEPTANCE-CONSEQUENCE-001 -->
**Acceptance SHALL promote only the candidate result belonging to the governed stage in which acceptance occurs.**

### GOV-14 — Semantic Defect Routing
<!-- section-id: GOV-14-SEMANTIC-DEFECT-ROUTING -->

<!-- DP020-GOV-14-SEMANTIC-DEFECT-ROUTING-001 -->
**A defect requiring persistent normative semantic change SHALL route to Design.**

### GOV-15 — Plan Defect Routing
<!-- section-id: GOV-15-PLAN-DEFECT-ROUTING -->

<!-- DP020-GOV-15-PLAN-DEFECT-ROUTING-001 -->
**A defect requiring realization-intent change without normative semantic change SHALL route to Plan.**

### GOV-16 — No Downstream Invention
<!-- section-id: GOV-16-NO-DOWNSTREAM-INVENTION -->

<!-- DP020-GOV-16-NO-DOWNSTREAM-INVENTION-001 -->
**A downstream Governance stage SHALL NOT create authority required from an upstream Governance stage.**

### GOV-17 — Governance Lineage
<!-- section-id: GOV-17-GOVERNANCE-LINEAGE -->

<!-- DP020-GOV-17-GOVERNANCE-LINEAGE-001 -->
**A completed Governance lifecycle SHALL preserve resolvable provenance from Design Proposal through Design, Plan, Build, and accepted repository state.**

### GOV-18 — Governed Work Provenance
<!-- section-id: GOV-18-GOVERNED-WORK-PROVENANCE -->

<!-- DP020-GOV-18-GOVERNED-WORK-PROVENANCE-001 -->
**Each governed realization work item SHALL resolve to accepted authority that requires or authorizes the work.**

### GOV-19 — Design Delta
<!-- section-id: GOV-19-DESIGN-DELTA -->

<!-- DP020-GOV-19-DESIGN-DELTA-001 -->
**An accepted Design result SHALL identify the normative authority created, amended, superseded, or withdrawn.**

### GOV-20 — Plan Coverage
<!-- section-id: GOV-20-PLAN-COVERAGE -->

<!-- DP020-GOV-20-PLAN-COVERAGE-001 -->
**An accepted Plan SHALL address each accepted Design obligation that requires governed realization work.**

### GOV-21 — Explicit Governed State
<!-- section-id: GOV-21-EXPLICIT-GOVERNED-STATE -->

<!-- DP020-GOV-21-EXPLICIT-GOVERNED-STATE-001 -->
**Governed-work state SHALL be explicitly represented rather than inferred solely from surrounding repository or platform state.**

### GOV-22 — Authority Lifecycle
<!-- section-id: GOV-22-AUTHORITY-LIFECYCLE -->

<!-- DP020-GOV-22-AUTHORITY-LIFECYCLE-001 -->
**Governance SHALL support creation, amendment, supersession, and withdrawal of accepted normative authority.**

### GOV-23 — Historical Resolution
<!-- section-id: GOV-23-HISTORICAL-RESOLUTION -->

<!-- DP020-GOV-23-HISTORICAL-RESOLUTION-001 -->
**Superseded or withdrawn normative authority SHALL remain historically resolvable.**

### GOV-24 — Identity Preservation
<!-- section-id: GOV-24-IDENTITY-PRESERVATION -->

<!-- DP020-GOV-24-IDENTITY-PRESERVATION-001 -->
**A normative identity SHALL NOT be reused in a manner that obscures previously accepted authority.**

### GOV-25 — Normative Requirement Identity
<!-- section-id: GOV-25-NORMATIVE-REQUIREMENT-IDENTITY -->

<!-- DP020-GOV-25-NORMATIVE-REQUIREMENT-IDENTITY-001 -->
**Each accepted normative obligation SHALL be represented by a stable machine-resolvable normative requirement identity.**

### GOV-26 — Evaluation Disposition
<!-- section-id: GOV-26-EVALUATION-DISPOSITION -->

<!-- DP020-GOV-26-EVALUATION-DISPOSITION-001 -->
**Each accepted normative requirement SHALL have governed Conformance and Assurance applicability, and a requirement with neither mechanical Conformance nor required Assurance SHALL have a governed rationale.**

### GOV-27 — Acceptance Authority
<!-- section-id: GOV-27-ACCEPTANCE-AUTHORITY -->

<!-- DP020-GOV-27-ACCEPTANCE-AUTHORITY-001 -->
**Governance acceptance SHALL depend only on authority accepted before the candidate result acquires the authority produced by that acceptance.**

### GOV-28 — Bounded Governed Authorization
<!-- section-id: GOV-28-BOUNDED-GOVERNED-AUTHORIZATION -->

<!-- DP020-GOV-28-BOUNDED-GOVERNED-AUTHORIZATION-001 -->
**A governed work item SHALL authorize only its explicitly governed scope and SHALL NOT independently authorize unrelated or successor work.**

## Primary Design Invariant
<!-- section-id: PRIMARY-DESIGN-INVARIANT -->

<!-- DP020-PRIMARY-DESIGN-INVARIANT-001 -->
**Governance SHALL transform non-authoritative design intent into accepted repository state through a traceable Design → Plan → Build lifecycle in which accepted normative obligations have stable requirement identities and governed evaluation dispositions, Design owns normative semantics, Plan owns realization intent, Build realizes only accepted Plan work, governed authorization remains bounded to explicit scope, acceptance is explicit and depends only on previously accepted authority, and downstream stages route upstream defects rather than invent missing authority.**

<!-- DP020-PRIMARY-DESIGN-INVARIANT-002 -->
All detailed Governance design shall preserve this invariant.

## Audit Questions
<!-- section-id: AUDIT-QUESTIONS -->

<!-- DP020-AUDIT-QUESTIONS-001 -->
The current repository should be audited against this proposal by determining:

<!-- DP020-AUDIT-QUESTIONS-002 -->
1. Which current workflows already perform Design, Plan, or Build responsibilities.

<!-- DP020-AUDIT-QUESTIONS-003 -->
2. Which workflows combine multiple Governance stages into one governed artifact.

<!-- DP020-AUDIT-QUESTIONS-004 -->
3. Which current mechanisms allow implementation to create de facto normative semantics.

<!-- DP020-AUDIT-QUESTIONS-005 -->
4. Which current artifacts function as accepted authority without explicit Governance acceptance.

<!-- DP020-AUDIT-QUESTIONS-006 -->
5. Which Plan or Build work lacks provenance to accepted authority.

<!-- DP020-AUDIT-QUESTIONS-007 -->
6. Which processes treat merge, issue closure, Conformance success, review approval, or downstream activity as implicit acceptance.

<!-- DP020-AUDIT-QUESTIONS-008 -->
7. Which normative changes bypass distinct Design governed work.

<!-- DP020-AUDIT-QUESTIONS-009 -->
8. Which Build activities require unresolved semantic decisions that belong in Design.

<!-- DP020-AUDIT-QUESTIONS-010 -->
9. Which Plan activities create semantics not accepted by Design.

<!-- DP020-AUDIT-QUESTIONS-011 -->
10. Which defects are currently repaired downstream rather than routed to the stage that owns them.

<!-- DP020-AUDIT-QUESTIONS-012 -->
11. Which accepted Designs lack complete realization coverage in Plan.

<!-- DP020-AUDIT-QUESTIONS-013 -->
12. Which superseded or withdrawn authority is not historically resolvable.

<!-- DP020-AUDIT-QUESTIONS-014 -->
13. Which governed state is inferred from GitHub platform state rather than explicitly represented.

<!-- DP020-AUDIT-QUESTIONS-015 -->
14. Whether the Audit / Normalize / Accept Design structure cleanly separates semantic discovery, normative production, and acceptance.

<!-- DP020-AUDIT-QUESTIONS-016 -->
15. Whether the Analyze / Specify / Accept Plan structure cleanly separates impact analysis, realization planning, and acceptance.

<!-- DP020-AUDIT-QUESTIONS-017 -->
16. Whether the Implement / Verify / Accept Build structure cleanly separates realization, evidence evaluation, and acceptance.

<!-- DP020-AUDIT-QUESTIONS-018 -->
17. Whether each candidate GOV requirement represents one independently identifiable obligation.

<!-- DP020-AUDIT-QUESTIONS-019 -->
18. Whether any candidate GOV requirement duplicates or logically follows from another.

<!-- DP020-AUDIT-QUESTIONS-020 -->
19. Which GOV requirements are mechanically enforceable through Conformance.

<!-- DP020-AUDIT-QUESTIONS-021 -->
20. Which GOV requirements require Assurance.

<!-- DP020-AUDIT-QUESTIONS-022 -->
21. What minimum Governance authority must be accepted before Conformance and Assurance lifecycle integration can be normalized.

## Explicitly Deferred Concerns
<!-- section-id: EXPLICITLY-DEFERRED-CONCERNS -->

<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-001 -->
The following concerns are intentionally outside this Governance proposal:

<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-002 -->
- exact GitHub issue schema;
<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-003 -->
- exact issue labels;
<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-004 -->
- detailed governed-state vocabulary;
<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-005 -->
- exact transition syntax;
<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-006 -->
- exact acceptance actor model;
<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-007 -->
- exact approval cardinality;
<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-008 -->
- detailed normative-requirement quality criteria;
<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-009 -->
- exact Conformance implementation;
<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-010 -->
- exact Assurance implementation;
<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-011 -->
- validation package architecture;
<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-012 -->
- review finding schema;
<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-013 -->
- implementation-language choices;
<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-014 -->
- migration execution details; and
<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-015 -->
- bootstrap sequencing.

<!-- DP020-EXPLICITLY-DEFERRED-CONCERNS-016 -->
These concerns may be defined by subordinate Governance authority or by Conformance and Assurance according to their delegated responsibilities.

## Relationship to Conformance and Assurance
<!-- section-id: RELATIONSHIP-TO-CONFORMANCE-AND-ASSURANC -->

<!-- DP020-RELATIONSHIP-TO-CONFORMANCE-AND-ASSURANC-001 -->
The Conformance Architecture Proposal shall define how objective mechanical enforcement operates under accepted normative authority.

<!-- DP020-RELATIONSHIP-TO-CONFORMANCE-AND-ASSURANC-002 -->
The Assurance Architecture Proposal shall define how governed semantic review and case-specific judgment operate under accepted normative authority.

<!-- DP020-RELATIONSHIP-TO-CONFORMANCE-AND-ASSURANC-003 -->
Governance may consume outputs from both keystones but shall not absorb their responsibilities.

<!-- DP020-RELATIONSHIP-TO-CONFORMANCE-AND-ASSURANC-004 -->
The Governance architecture should be normalized before lifecycle coupling to Conformance and Assurance is accepted.

## FS0-Core and Functional Sets
<!-- section-id: FS0-CORE-AND-FUNCTIONAL-SETS -->

<!-- DP020-FS0-CORE-AND-FUNCTIONAL-SETS-001 -->
FS0-Core is the standalone core functional set. It implements the minimum complete repository-framework runtime and development workflow required for every later functional set to operate.

<!-- DP020-FS0-CORE-AND-FUNCTIONAL-SETS-002 -->
Every later functional set technically depends on FS0-Core and extends the accepted Core-based system. Later functional sets are identified by functionality rather than FS1/FS2-style generations.

<!-- DP020-FS0-CORE-AND-FUNCTIONAL-SETS-003 -->
Planning identifies functional sets incrementally. It need not decompose the entire Design into a future implementation graph in one pass.

## Functional-Set Artifact Boundary
<!-- section-id: FUNCTIONAL-SET-ARTIFACT-BOUNDARY -->

<!-- DP020-FUNCTIONAL-SET-ARTIFACT-BOUNDARY-001 -->
Each functional set has an implementation-ordered plan directory containing `functional-set.json` and `plan.json`.

<!-- DP020-FUNCTIONAL-SET-ARTIFACT-BOUNDARY-002 -->
`functional-set.json` selects the Design Proposal statement IDs that define the functional scope.

<!-- DP020-FUNCTIONAL-SET-ARTIFACT-BOUNDARY-003 -->
`plan.json` owns decomposition and distillation of that selected Design into repository normative requirements, exact files, pseudo-code, sequencing, and validation intent.

<!-- DP020-FUNCTIONAL-SET-ARTIFACT-BOUNDARY-004 -->
No one-to-one relationship is required between Design statement IDs and normative requirements.
