---
doc_id: DP-010
title: Framework Contract Architecture Proposal
status: planning-ready
depends_on: []
artifact_type: design-proposal
canonical_format: markdown
---
# Framework Contract Architecture Proposal

## Status

**Section ID:** `STATUS`

**DP010-STATUS-001**
Planning-ready Design Proposal.

## Purpose

**Section ID:** `PURPOSE`

**DP010-PURPOSE-001**
Define the foundational authority topology of the repository framework.

## Context

**Section ID:** `CONTEXT`

**DP010-CONTEXT-001**
The framework requires explicit authority boundaries among Governance, Conformance, Assurance, implementation, and product authority.

## Goals

**Section ID:** `GOALS`

**DP010-GOALS-001**
- Preserve the domain architecture and authority boundaries defined by this proposal.
**DP010-GOALS-002**
- Make the proposal consumable by incremental functional-set Planning.
**DP010-GOALS-003**
- Keep Design statement identity distinct from repository normative identity.

## Non-Goals

**Section ID:** `NON-GOALS`

**DP010-NON-GOALS-001**
- Define one complete implementation plan for the entire proposal.
**DP010-NON-GOALS-002**
- Assign repository normative IDs during Design.
**DP010-NON-GOALS-003**
- Define file-level pseudo-code in Design unless it is itself a semantic constraint.

## Requirements

**Section ID:** `REQUIREMENTS`

**DP010-REQUIREMENTS-001**
The detailed Design below contains addressable Design statements. Statement IDs are non-normative proposal references. `functional-set.json` selects them; `plan.json` owns decomposition and normative distillation.

## Constraints

**Section ID:** `CONSTRAINTS`

**DP010-CONSTRAINTS-001**
This proposal remains subordinate to its declared Design dependencies and shall not silently assume authority outside them.

## Architecture

**Section ID:** `ARCHITECTURE`

**DP010-ARCHITECTURE-001**
The detailed Design below is semantic input to Planning and may be realized over multiple functional sets.

## Behavior

**Section ID:** `BEHAVIOR`

**DP010-BEHAVIOR-001**
Planning may consume a bounded subset of this proposal in one functional set; implementation of the entire proposal in one pass is not required.

## Interfaces and Boundaries

**Section ID:** `INTERFACES-AND-BOUNDARIES`

**DP010-INTERFACES-AND-BOUNDARIES-001**
Design defines meaning. `functional-set.json` defines selected Design scope. `plan.json` defines normative decomposition and exact implementation intent. Build produces syntactically correct, validated, operational code.

## Invariants

**Section ID:** `INVARIANTS`

**DP010-INVARIANTS-001**
- Design statement IDs remain non-normative.
**DP010-INVARIANTS-002**
- Planning owns normative distillation and implementation intent.
**DP010-INVARIANTS-003**
- Build shall not invent missing Design semantics or missing Plan intent.

## Alternatives Considered

**Section ID:** `ALTERNATIVES-CONSIDERED`

**DP010-ALTERNATIVES-CONSIDERED-001**
Domain-specific alternatives remain in the detailed Design. The revised workflow rejects collapsing Design, Planning, and Build into one artifact or stage.

## Risks and Tradeoffs

**Section ID:** `RISKS-AND-TRADEOFFS`

**DP010-RISKS-AND-TRADEOFFS-001**
Incremental realization may expose missing or ambiguous Design later; those defects must route to Design rather than being silently invented during Planning or Build.

## Open Questions

**Section ID:** `OPEN-QUESTIONS`

**DP010-OPEN-QUESTIONS-001**
No blocking workflow-format questions remain. Domain-specific open questions are retained in the detailed Design.

## Acceptance Criteria

**Section ID:** `ACCEPTANCE-CRITERIA`

**DP010-ACCEPTANCE-CRITERIA-001**
This proposal is planning-ready when its required sections are complete, its detailed semantics remain coherent with declared dependencies, and its Design statements are addressable.

# Detailed Design

## Objective

**Section ID:** `OBJECTIVE`

**DP010-OBJECTIVE-001**
The repository framework shall define one foundational Framework Contract that authorizes and bounds three authority-bearing keystones:

**DP010-OBJECTIVE-002**
1. Governance
**DP010-OBJECTIVE-003**
2. Conformance
**DP010-OBJECTIVE-004**
3. Assurance

**DP010-OBJECTIVE-005**
The Framework Contract shall establish:

**DP010-OBJECTIVE-006**
- where framework authority resides;
**DP010-OBJECTIVE-007**
- what powers each keystone may exercise;
**DP010-OBJECTIVE-008**
- what powers each keystone may not exercise;
**DP010-OBJECTIVE-009**
- how persistent normative authority may change;
**DP010-OBJECTIVE-010**
- how mechanical enforcement remains subordinate to accepted authority;
**DP010-OBJECTIVE-011**
- how semantic review remains subordinate to accepted authority;
**DP010-OBJECTIVE-012**
- how derived framework behavior remains traceable to accepted authority;
**DP010-OBJECTIVE-013**
- how product authority remains subordinate to framework authority; and
**DP010-OBJECTIVE-014**
- how authority relationships remain explicit and machine-resolvable.

**DP010-OBJECTIVE-015**
The primary architectural objective is separation of responsibility under explicit accepted authority.

## Foundational Model

**Section ID:** `FOUNDATIONAL-MODEL`

**DP010-FOUNDATIONAL-MODEL-001**
`repo/` contains accepted repository-framework normative authority.

**DP010-FOUNDATIONAL-MODEL-002**
The Framework Contract is the foundational normative layer within `repo/`.

**DP010-FOUNDATIONAL-MODEL-003**
The Framework Contract authorizes and bounds:

**DP010-FOUNDATIONAL-MODEL-004**
- Governance;
**DP010-FOUNDATIONAL-MODEL-005**
- Conformance; and
**DP010-FOUNDATIONAL-MODEL-006**
- Assurance.

**DP010-FOUNDATIONAL-MODEL-007**
Those keystones collectively support the governed framework and maintained product.

**DP010-FOUNDATIONAL-MODEL-008**
The authority topology is:

**DP010-FOUNDATIONAL-MODEL-009**
**repo/**
**DP010-FOUNDATIONAL-MODEL-010**
→ Framework Contract
**DP010-FOUNDATIONAL-MODEL-011**
→ Governance / Conformance / Assurance
**DP010-FOUNDATIONAL-MODEL-012**
→ governed framework and maintained product

**DP010-FOUNDATIONAL-MODEL-013**
Implementation does not acquire authority merely because it exists.

## Framework Authority

**Section ID:** `FRAMEWORK-AUTHORITY`

**DP010-FRAMEWORK-AUTHORITY-001**
Framework authority is accepted normative authority that defines the repository framework.

**DP010-FRAMEWORK-AUTHORITY-002**
Accepted repository-framework normative authority shall reside within `repo/`.

**DP010-FRAMEWORK-AUTHORITY-003**
Framework authority may define:

**DP010-FRAMEWORK-AUTHORITY-004**
- authority relationships;
**DP010-FRAMEWORK-AUTHORITY-005**
- framework structure;
**DP010-FRAMEWORK-AUTHORITY-006**
- artifact roles;
**DP010-FRAMEWORK-AUTHORITY-007**
- keystone powers;
**DP010-FRAMEWORK-AUTHORITY-008**
- provenance obligations;
**DP010-FRAMEWORK-AUTHORITY-009**
- framework/product relationships; and
**DP010-FRAMEWORK-AUTHORITY-010**
- framework evolution constraints.

**DP010-FRAMEWORK-AUTHORITY-011**
Implementation may realize framework authority but shall not independently establish, extend, or amend it.

**DP010-FRAMEWORK-AUTHORITY-012**
Normative authority shall not arise solely from:

**DP010-FRAMEWORK-AUTHORITY-013**
- implementation behavior;
**DP010-FRAMEWORK-AUTHORITY-014**
- validation behavior;
**DP010-FRAMEWORK-AUTHORITY-015**
- review findings;
**DP010-FRAMEWORK-AUTHORITY-016**
- generated artifacts;
**DP010-FRAMEWORK-AUTHORITY-017**
- workflow convention;
**DP010-FRAMEWORK-AUTHORITY-018**
- historical repository state; or
**DP010-FRAMEWORK-AUTHORITY-019**
- product behavior.

## Framework Contract

**Section ID:** `FRAMEWORK-CONTRACT`

**DP010-FRAMEWORK-CONTRACT-001**
The Framework Contract defines the foundational authority topology of the repository framework.

**DP010-FRAMEWORK-CONTRACT-002**
It shall establish:

**DP010-FRAMEWORK-CONTRACT-003**
- `repo/` as the authoritative framework namespace;
**DP010-FRAMEWORK-CONTRACT-004**
- Governance, Conformance, and Assurance as the three authority-bearing keystones;
**DP010-FRAMEWORK-CONTRACT-005**
- the authority delegated to each keystone;
**DP010-FRAMEWORK-CONTRACT-006**
- the authority prohibited to each keystone;
**DP010-FRAMEWORK-CONTRACT-007**
- the separation of keystone responsibilities;
**DP010-FRAMEWORK-CONTRACT-008**
- the permitted direction of normative authority flow;
**DP010-FRAMEWORK-CONTRACT-009**
- foundational provenance obligations;
**DP010-FRAMEWORK-CONTRACT-010**
- the prohibition against implicit authority creation;
**DP010-FRAMEWORK-CONTRACT-011**
- the relationship between framework authority and product authority; and
**DP010-FRAMEWORK-CONTRACT-012**
- requirements for explicit, resolvable authority representation;
**DP010-FRAMEWORK-CONTRACT-013**
- default-deny authorization of maintained governed state;
**DP010-FRAMEWORK-CONTRACT-014**
- single controlling semantic ownership; and
**DP010-FRAMEWORK-CONTRACT-015**
- acyclic normative authority dependency.

**DP010-FRAMEWORK-CONTRACT-016**
The Framework Contract shall remain intentionally compact.

**DP010-FRAMEWORK-CONTRACT-017**
It shall define authority and boundaries rather than detailed operating mechanics.

**DP010-FRAMEWORK-CONTRACT-018**
Subordinate framework specifications shall define how the keystones perform their authorized responsibilities.

## Authority-Bearing Keystones

**Section ID:** `AUTHORITY-BEARING-KEYSTONES`

**DP010-AUTHORITY-BEARING-KEYSTONES-001**
The repository framework shall define exactly three authority-bearing keystones:

**DP010-AUTHORITY-BEARING-KEYSTONES-002**
1. Governance
**DP010-AUTHORITY-BEARING-KEYSTONES-003**
2. Conformance
**DP010-AUTHORITY-BEARING-KEYSTONES-004**
3. Assurance

**DP010-AUTHORITY-BEARING-KEYSTONES-005**
Supporting mechanisms may exist.

**DP010-AUTHORITY-BEARING-KEYSTONES-006**
Supporting mechanisms shall operate only under authority delegated through accepted repository-framework authority.

**DP010-AUTHORITY-BEARING-KEYSTONES-007**
A supporting mechanism shall not independently acquire authority equivalent to a keystone.

## Governance

**Section ID:** `GOVERNANCE`

**DP010-GOVERNANCE-001**
Governance is the framework mechanism responsible for persistent normative change.

**DP010-GOVERNANCE-002**
Governance answers:

**DP010-GOVERNANCE-003**
**What accepted normative authority may be created, changed, superseded, or withdrawn?**

**DP010-GOVERNANCE-004**
Governance may:

**DP010-GOVERNANCE-005**
- create or change accepted framework authority;
**DP010-GOVERNANCE-006**
- create or change accepted product authority; and
**DP010-GOVERNANCE-007**
- consume Conformance or Assurance findings when persistent normative change is required.

**DP010-GOVERNANCE-008**
Governance shall not:

**DP010-GOVERNANCE-009**
- derive normative authority from implementation behavior;
**DP010-GOVERNANCE-010**
- derive normative authority from validation behavior;
**DP010-GOVERNANCE-011**
- treat Assurance findings as persistent normative authority without governed acceptance; or
**DP010-GOVERNANCE-012**
- substitute workflow completion for required Conformance or Assurance.

**DP010-GOVERNANCE-013**
Persistent changes to accepted normative authority shall occur only through Governance.

**DP010-GOVERNANCE-014**
Because repository-framework authority is normative authority, persistent changes to the Framework Contract or keystone authority are themselves subject to Governance.

**DP010-GOVERNANCE-015**
Detailed Governance lifecycle, stage, artifact, transition, and acceptance mechanics belong in the Governance Architecture Proposal.

## Conformance

**Section ID:** `CONFORMANCE`

**DP010-CONFORMANCE-001**
Conformance is the framework mechanism responsible for mechanical enforcement of accepted normative authority.

**DP010-CONFORMANCE-002**
Conformance answers:

**DP010-CONFORMANCE-003**
**Does observable state satisfy the mechanically decidable obligations established by accepted normative authority?**

**DP010-CONFORMANCE-004**
Conformance may:

**DP010-CONFORMANCE-005**
- mechanically evaluate observable state;
**DP010-CONFORMANCE-006**
- reject mechanically nonconforming state; and
**DP010-CONFORMANCE-007**
- produce mechanical findings and evidence.

**DP010-CONFORMANCE-008**
Conformance shall not:

**DP010-CONFORMANCE-009**
- create normative requirements;
**DP010-CONFORMANCE-010**
- extend accepted normative semantics;
**DP010-CONFORMANCE-011**
- convert implementation preference into normative enforcement;
**DP010-CONFORMANCE-012**
- infer normative authority from historical behavior; or
**DP010-CONFORMANCE-013**
- claim semantic certainty where mechanical evaluation cannot decide the matter.

**DP010-CONFORMANCE-014**
Mechanical enforcement of accepted normative authority shall occur only through Conformance.

**DP010-CONFORMANCE-015**
Detailed validation hierarchy, packages, primitives, tests, fixtures, runners, evidence, correspondence, and enforcement-provenance mechanics belong in the Conformance Architecture Proposal.

## Assurance

**Section ID:** `ASSURANCE`

**DP010-ASSURANCE-001**
Assurance is the framework mechanism responsible for governed semantic review and case-specific semantic judgment.

**DP010-ASSURANCE-002**
Assurance answers:

**DP010-ASSURANCE-003**
**Is the authority, realization, evidence, or application under review semantically adequate and sufficiently justified?**

**DP010-ASSURANCE-004**
Assurance may:

**DP010-ASSURANCE-005**
- evaluate semantic properties that Conformance cannot decide;
**DP010-ASSURANCE-006**
- evaluate the sufficiency of evidence;
**DP010-ASSURANCE-007**
- identify ambiguity, contradiction, omission, or inappropriate interpretation; and
**DP010-ASSURANCE-008**
- issue case-specific semantic findings.

**DP010-ASSURANCE-009**
Assurance shall not:

**DP010-ASSURANCE-010**
- create persistent normative authority;
**DP010-ASSURANCE-011**
- amend accepted normative authority;
**DP010-ASSURANCE-012**
- extend accepted normative semantics through review;
**DP010-ASSURANCE-013**
- replace Governance as the mechanism for persistent normative change; or
**DP010-ASSURANCE-014**
- replace Conformance for mechanically decidable enforcement.

**DP010-ASSURANCE-015**
Governed semantic review and case-specific semantic judgment shall occur only through Assurance.

**DP010-ASSURANCE-016**
An Assurance finding may affect disposition of the specific case under review where authorized by accepted framework authority.

**DP010-ASSURANCE-017**
An Assurance finding shall not independently create or amend persistent normative authority.

**DP010-ASSURANCE-018**
A finding that requires persistent normative change shall return through Governance.

**DP010-ASSURANCE-019**
Detailed Assurance artifacts, reviewer roles, finding taxonomy, interpretation rules, review lifecycle, evidence requirements, and adjudication mechanics belong in the Assurance Architecture Proposal.

## Keystone Separation

**Section ID:** `KEYSTONE-SEPARATION`

**DP010-KEYSTONE-SEPARATION-001**
Each keystone has one primary authority domain.

| Keystone | Authority Domain |
| --- | --- |
| Governance | persistent normative change |
| Conformance | mechanical normative enforcement |
| Assurance | governed semantic review and case-specific judgment |

**DP010-KEYSTONE-SEPARATION-002**
A keystone shall exercise only authority delegated by accepted repository-framework authority.

**DP010-KEYSTONE-SEPARATION-003**
A keystone shall not independently exercise authority reserved to another keystone.

**DP010-KEYSTONE-SEPARATION-004**
A supporting mechanism shall not bypass keystone separation by exercising equivalent authority under another name.

## Authority Flow

**Section ID:** `AUTHORITY-FLOW`

**DP010-AUTHORITY-FLOW-001**
Normative authority flows through the framework as follows:

**DP010-AUTHORITY-FLOW-002**
**Framework Contract**
**DP010-AUTHORITY-FLOW-003**
→ delegates authority to Governance, Conformance, and Assurance

**DP010-AUTHORITY-FLOW-004**
**Governance**
**DP010-AUTHORITY-FLOW-005**
→ creates or changes accepted normative authority

**DP010-AUTHORITY-FLOW-006**
**Accepted normative authority**
**DP010-AUTHORITY-FLOW-007**
→ governs realization
**DP010-AUTHORITY-FLOW-008**
→ authorizes mechanical Conformance
**DP010-AUTHORITY-FLOW-009**
→ provides the semantic basis for Assurance

**DP010-AUTHORITY-FLOW-010**
**Conformance**
**DP010-AUTHORITY-FLOW-011**
→ produces mechanical findings and evidence

**DP010-AUTHORITY-FLOW-012**
**Assurance**
**DP010-AUTHORITY-FLOW-013**
→ produces semantic findings

**DP010-AUTHORITY-FLOW-014**
**Persistent normative change**
**DP010-AUTHORITY-FLOW-015**
→ returns through Governance

**DP010-AUTHORITY-FLOW-016**
Authority flow and implementation dependency flow are distinct.

**DP010-AUTHORITY-FLOW-017**
Implementation structure shall not obscure, replace, or invert normative authority.

## Authority Inversion

**Section ID:** `AUTHORITY-INVERSION`

**DP010-AUTHORITY-INVERSION-001**
Authority inversion occurs when a subordinate or derived artifact or mechanism is treated as normative authority without Governance having established that authority.

**DP010-AUTHORITY-INVERSION-002**
The framework shall prohibit the following authority inversions:

**DP010-AUTHORITY-INVERSION-003**
**implementation behavior → normative authority**

**DP010-AUTHORITY-INVERSION-004**
**validation behavior → normative authority**

**DP010-AUTHORITY-INVERSION-005**
**review finding → persistent normative authority**

**DP010-AUTHORITY-INVERSION-006**
**generated artifact → normative authority**

**DP010-AUTHORITY-INVERSION-007**
**workflow convention → normative authority**

**DP010-AUTHORITY-INVERSION-008**
**historical repository state → normative authority**

**DP010-AUTHORITY-INVERSION-009**
**product behavior → framework authority**

**DP010-AUTHORITY-INVERSION-010**
Existing behavior may be incorporated into normative authority only through Governance.

**DP010-AUTHORITY-INVERSION-011**
Historical or bootstrap behavior shall not become normative solely because preserving it is convenient.

## Framework Authority and Product Authority

**Section ID:** `FRAMEWORK-AUTHORITY-AND-PRODUCT-AUTHORIT`

**DP010-FRAMEWORK-AUTHORITY-AND-PRODUCT-AUTHORIT-001**
Framework authority and product authority are distinct.

**DP010-FRAMEWORK-AUTHORITY-AND-PRODUCT-AUTHORIT-002**
Framework authority defines how the repository framework operates.

**DP010-FRAMEWORK-AUTHORITY-AND-PRODUCT-AUTHORIT-003**
Product authority defines accepted normative semantics for the maintained product.

**DP010-FRAMEWORK-AUTHORITY-AND-PRODUCT-AUTHORIT-004**
Framework authority defines how product authority is:

**DP010-FRAMEWORK-AUTHORITY-AND-PRODUCT-AUTHORIT-005**
- created or changed;
**DP010-FRAMEWORK-AUTHORITY-AND-PRODUCT-AUTHORIT-006**
- mechanically enforced;
**DP010-FRAMEWORK-AUTHORITY-AND-PRODUCT-AUTHORIT-007**
- semantically reviewed; and
**DP010-FRAMEWORK-AUTHORITY-AND-PRODUCT-AUTHORIT-008**
- related to product realization.

**DP010-FRAMEWORK-AUTHORITY-AND-PRODUCT-AUTHORIT-009**
Neither product authority nor product implementation shall independently define or amend repository-framework authority.

**DP010-FRAMEWORK-AUTHORITY-AND-PRODUCT-AUTHORIT-010**
Product implementation remains subordinate to applicable framework authority and product authority.

## Provenance

**Section ID:** `PROVENANCE`

**DP010-PROVENANCE-001**
Every maintained derived framework primitive shall resolve to accepted normative authority that authorizes its existence or use.

**DP010-PROVENANCE-002**
For a derived framework primitive, it shall be possible to determine:

**DP010-PROVENANCE-003**
- that the primitive is derived rather than normative;
**DP010-PROVENANCE-004**
- which accepted normative authority authorizes it; and
**DP010-PROVENANCE-005**
- which keystone responsibility it serves.

**DP010-PROVENANCE-006**
The absence of resolvable provenance shall be treated as a framework defect.

**DP010-PROVENANCE-007**
Missing provenance shall not permit authority to be inferred from implementation, convention, or historical behavior.

**DP010-PROVENANCE-008**
Detailed primitive identity, provenance representation, and correspondence mechanics belong in subordinate framework specifications.

## Explicit Authority Representation

**Section ID:** `EXPLICIT-AUTHORITY-REPRESENTATION`

**DP010-EXPLICIT-AUTHORITY-REPRESENTATION-001**
Accepted repository-framework authority shall have stable machine-resolvable identities.

**DP010-EXPLICIT-AUTHORITY-REPRESENTATION-002**
Delegated authority relationships shall be resolvable without inference from non-authoritative repository state.

**DP010-EXPLICIT-AUTHORITY-REPRESENTATION-003**
A human or automated consumer shall not be required to infer authority from:

**DP010-EXPLICIT-AUTHORITY-REPRESENTATION-004**
- implementation behavior;
**DP010-EXPLICIT-AUTHORITY-REPRESENTATION-005**
- file proximity;
**DP010-EXPLICIT-AUTHORITY-REPRESENTATION-006**
- historical convention;
**DP010-EXPLICIT-AUTHORITY-REPRESENTATION-007**
- generated output;
**DP010-EXPLICIT-AUTHORITY-REPRESENTATION-008**
- reviewer preference; or
**DP010-EXPLICIT-AUTHORITY-REPRESENTATION-009**
- other non-authoritative context.

**DP010-EXPLICIT-AUTHORITY-REPRESENTATION-010**
Automated tooling and AI agents are subject to the same authority boundaries as human contributors.

**DP010-EXPLICIT-AUTHORITY-REPRESENTATION-011**
The ability to inspect or modify repository state does not grant additional authority.

## Framework Contract and Keystone Specifications

**Section ID:** `FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC`

**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-001**
The Framework Contract defines:

**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-002**
- framework authority;
**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-003**
- keystone delegation;
**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-004**
- authority boundaries;
**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-005**
- authority flow;
**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-006**
- provenance obligations;
**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-007**
- framework/product authority separation; and
**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-008**
- explicit authority representation.

**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-009**
The Governance Architecture Proposal shall define how persistent normative change operates.

**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-010**
The Conformance Architecture Proposal shall define how mechanical normative enforcement operates.

**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-011**
The Assurance Architecture Proposal shall define how governed semantic review operates.

**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-012**
A subordinate framework specification shall not redefine or exceed authority delegated by the Framework Contract.

**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-013**
Maintained governed framework state shall require accepted authorization or an explicitly governed extension point.

**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-014**
Each independently governed framework semantic invariant shall have one controlling normative owner.

**DP010-FRAMEWORK-CONTRACT-AND-KEYSTONE-SPECIFIC-015**
Normative authority shall not depend for its authority on a cycle of normative dependencies.

## Candidate Foundational Requirements

**Section ID:** `CANDIDATE-FOUNDATIONAL-REQUIREMENTS`

**DP010-CANDIDATE-FOUNDATIONAL-REQUIREMENTS-001**
The following proposal-local statements are Design input. Their labels are non-normative; Planning may distill repository normative requirements from any combination of selected Design statements.

### FC-01 — Framework Authority Location

**Section ID:** `FC-01-FRAMEWORK-AUTHORITY-LOCATION`

**DP010-FC-01-FRAMEWORK-AUTHORITY-LOCATION-001**
**Accepted repository-framework normative authority SHALL reside within `repo/`.**

### FC-02 — Framework Contract Role

**Section ID:** `FC-02-FRAMEWORK-CONTRACT-ROLE`

**DP010-FC-02-FRAMEWORK-CONTRACT-ROLE-001**
**The Framework Contract SHALL define the foundational authority topology of the repository framework.**

### FC-03 — Keystone Set

**Section ID:** `FC-03-KEYSTONE-SET`

**DP010-FC-03-KEYSTONE-SET-001**
**The repository framework SHALL define Governance, Conformance, and Assurance as its three authority-bearing keystones.**

### FC-04 — Delegated Authority

**Section ID:** `FC-04-DELEGATED-AUTHORITY`

**DP010-FC-04-DELEGATED-AUTHORITY-001**
**A keystone SHALL exercise only authority delegated by accepted repository-framework authority.**

### FC-05 — Governance Exclusivity

**Section ID:** `FC-05-GOVERNANCE-EXCLUSIVITY`

**DP010-FC-05-GOVERNANCE-EXCLUSIVITY-001**
**Persistent changes to accepted normative authority SHALL occur only through Governance.**

### FC-06 — Conformance Exclusivity

**Section ID:** `FC-06-CONFORMANCE-EXCLUSIVITY`

**DP010-FC-06-CONFORMANCE-EXCLUSIVITY-001**
**Mechanical enforcement of accepted normative authority SHALL occur only through Conformance.**

### FC-07 — Assurance Exclusivity

**Section ID:** `FC-07-ASSURANCE-EXCLUSIVITY`

**DP010-FC-07-ASSURANCE-EXCLUSIVITY-001**
**Governed semantic review and case-specific semantic judgment SHALL occur only through Assurance.**

### FC-08 — Assurance Persistence Boundary

**Section ID:** `FC-08-ASSURANCE-PERSISTENCE-BOUNDARY`

**DP010-FC-08-ASSURANCE-PERSISTENCE-BOUNDARY-001**
**An Assurance finding SHALL NOT independently create or amend persistent normative authority.**

### FC-09 — Keystone Separation

**Section ID:** `FC-09-KEYSTONE-SEPARATION`

**DP010-FC-09-KEYSTONE-SEPARATION-001**
**A keystone SHALL NOT independently exercise authority reserved to another keystone.**

### FC-10 — Derived Provenance

**Section ID:** `FC-10-DERIVED-PROVENANCE`

**DP010-FC-10-DERIVED-PROVENANCE-001**
**Every maintained derived framework primitive SHALL resolve to accepted normative authority that authorizes its existence or use.**

### FC-11 — No Implicit Authority

**Section ID:** `FC-11-NO-IMPLICIT-AUTHORITY`

**DP010-FC-11-NO-IMPLICIT-AUTHORITY-001**
**Normative authority SHALL NOT arise solely from the existence or behavior of a non-normative repository artifact or mechanism.**

### FC-12 — Product Subordination

**Section ID:** `FC-12-PRODUCT-SUBORDINATION`

**DP010-FC-12-PRODUCT-SUBORDINATION-001**
**Neither product authority nor product implementation SHALL independently define or amend repository-framework authority.**

### FC-13 — Authority Identity

**Section ID:** `FC-13-AUTHORITY-IDENTITY`

**DP010-FC-13-AUTHORITY-IDENTITY-001**
**Accepted repository-framework authority SHALL have stable machine-resolvable identities.**

### FC-14 — Delegation Resolution

**Section ID:** `FC-14-DELEGATION-RESOLUTION`

**DP010-FC-14-DELEGATION-RESOLUTION-001**
**Delegated authority relationships SHALL be resolvable without inference from non-authoritative repository state.**

### FC-15 — Default-Deny Maintained State

**Section ID:** `FC-15-DEFAULT-DENY-MAINTAINED-STATE`

**DP010-FC-15-DEFAULT-DENY-MAINTAINED-STATE-001**
**Maintained governed framework state SHALL require accepted authorization or an explicitly governed extension point.**

### FC-16 — Single Semantic Owner

**Section ID:** `FC-16-SINGLE-SEMANTIC-OWNER`

**DP010-FC-16-SINGLE-SEMANTIC-OWNER-001**
**Each independently governed framework semantic invariant SHALL have one controlling normative owner.**

### FC-17 — Acyclic Normative Dependency

**Section ID:** `FC-17-ACYCLIC-NORMATIVE-DEPENDENCY`

**DP010-FC-17-ACYCLIC-NORMATIVE-DEPENDENCY-001**
**Normative authority SHALL NOT depend for its authority on a cycle of normative dependencies.**

## Primary Design Invariant

**Section ID:** `PRIMARY-DESIGN-INVARIANT`

**DP010-PRIMARY-DESIGN-INVARIANT-001**
**The authoritative `repo/` framework SHALL define and bound Governance, Conformance, and Assurance such that persistent normative authority changes only through Governance, mechanical normative enforcement occurs only through Conformance, governed semantic review occurs only through Assurance, maintained governed state is positively authorized, each independently governed semantic invariant has one controlling normative owner, normative authority does not depend on circular normative dependencies, and derived framework behavior remains subordinate and traceable to accepted normative authority.**

**DP010-PRIMARY-DESIGN-INVARIANT-002**
All subordinate framework design shall preserve this invariant.

## Audit Questions

**Section ID:** `AUDIT-QUESTIONS`

**DP010-AUDIT-QUESTIONS-001**
The current repository should be audited against this proposal by determining:

**DP010-AUDIT-QUESTIONS-002**
1. Which current `repo/` specifications already express candidate Framework Contract authority.

**DP010-AUDIT-QUESTIONS-003**
2. Which framework semantics exist only in implementation, validation, workflow automation, review behavior, generated artifacts, or historical convention.

**DP010-AUDIT-QUESTIONS-004**
3. Which existing normative requirements combine Framework Contract concerns with Governance, Conformance, Assurance, or product-specific mechanics.

**DP010-AUDIT-QUESTIONS-005**
4. Which current authority relationships permit authority inversion.

**DP010-AUDIT-QUESTIONS-006**
5. Which current mechanisms exercise authority reserved to another keystone.

**DP010-AUDIT-QUESTIONS-007**
6. Which artifacts or behaviors function as de facto normative authority without an accepted normative owner.

**DP010-AUDIT-QUESTIONS-008**
7. Which derived framework primitives lack resolvable provenance to accepted normative authority.

**DP010-AUDIT-QUESTIONS-009**
8. Which product authority or implementation improperly defines framework authority.

**DP010-AUDIT-QUESTIONS-010**
9. Which current normative requirements are too compound, ambiguous, or implementation-specific to serve as clean authority anchors.

**DP010-AUDIT-QUESTIONS-011**
10. Which current framework behaviors represent intended target semantics and which represent bootstrap or historical behavior.

**DP010-AUDIT-QUESTIONS-012**
11. Whether each candidate foundational requirement represents one independently identifiable obligation.

**DP010-AUDIT-QUESTIONS-013**
12. Whether any candidate foundational requirement duplicates or logically subsumes another.

**DP010-AUDIT-QUESTIONS-014**
13. Which candidate foundational requirements are mechanically enforceable through Conformance.

**DP010-AUDIT-QUESTIONS-015**
14. Which candidate foundational requirements require Assurance.

**DP010-AUDIT-QUESTIONS-016**
15. What minimum Framework Contract authority must be accepted before Governance, Conformance, and Assurance can be normalized without circular authority.

## Explicitly Deferred Concerns

**Section ID:** `EXPLICITLY-DEFERRED-CONCERNS`

**DP010-EXPLICITLY-DEFERRED-CONCERNS-001**
The following concerns are intentionally outside the Framework Contract:

**DP010-EXPLICITLY-DEFERRED-CONCERNS-002**
- detailed normative-requirement quality rules;
**DP010-EXPLICITLY-DEFERRED-CONCERNS-003**
- Governance lifecycle details;
**DP010-EXPLICITLY-DEFERRED-CONCERNS-004**
- Design, Plan, and Build stage mechanics;
**DP010-EXPLICITLY-DEFERRED-CONCERNS-005**
- governed-work issue structure;
**DP010-EXPLICITLY-DEFERRED-CONCERNS-006**
- Conformance hierarchy details;
**DP010-EXPLICITLY-DEFERRED-CONCERNS-007**
- validation package design;
**DP010-EXPLICITLY-DEFERRED-CONCERNS-008**
- validation primitive taxonomy;
**DP010-EXPLICITLY-DEFERRED-CONCERNS-009**
- test and fixture architecture;
**DP010-EXPLICITLY-DEFERRED-CONCERNS-010**
- Assurance review mechanics;
**DP010-EXPLICITLY-DEFERRED-CONCERNS-011**
- reviewer assignment;
**DP010-EXPLICITLY-DEFERRED-CONCERNS-012**
- finding taxonomy;
**DP010-EXPLICITLY-DEFERRED-CONCERNS-013**
- migration mechanics;
**DP010-EXPLICITLY-DEFERRED-CONCERNS-014**
- bootstrap accommodations; and
**DP010-EXPLICITLY-DEFERRED-CONCERNS-015**
- successor-generation construction mechanics.

**DP010-EXPLICITLY-DEFERRED-CONCERNS-016**
These concerns may be governed by subordinate framework authority but shall remain consistent with the Framework Contract.

## Follow-On Design Proposals

**Section ID:** `FOLLOW-ON-DESIGN-PROPOSALS`

**DP010-FOLLOW-ON-DESIGN-PROPOSALS-001**
This proposal establishes the authority boundaries for three follow-on proposals:

**DP010-FOLLOW-ON-DESIGN-PROPOSALS-002**
1. Governance Architecture Proposal
**DP010-FOLLOW-ON-DESIGN-PROPOSALS-003**
2. Conformance Architecture Proposal
**DP010-FOLLOW-ON-DESIGN-PROPOSALS-004**
3. Assurance Architecture Proposal

**DP010-FOLLOW-ON-DESIGN-PROPOSALS-005**
Those proposals shall not assume authority that the Framework Contract does not delegate.

**DP010-FOLLOW-ON-DESIGN-PROPOSALS-006**
The Framework Contract should therefore be normalized before the keystone architectures are accepted.
