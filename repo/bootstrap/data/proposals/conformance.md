---
doc_id: DP-030
title: Conformance Architecture Proposal
status: planning-ready
depends_on:
  - DP-010
  - DP-020
artifact_type: design-proposal
canonical_format: markdown
---
# Conformance Architecture Proposal

## Status

**Section ID:** `STATUS`

**DP030-STATUS-001**
Planning-ready Design Proposal.

## Purpose

**Section ID:** `PURPOSE`

**DP030-PURPOSE-001**
Define mechanical enforcement for accepted authority and for objective Design, Plan, and Build checks.

## Context

**Section ID:** `CONTEXT`

**DP030-CONTEXT-001**
Conformance must mechanically validate not only accepted normative authority but also the structural and executable contracts needed by the revised workflow.

## Goals

**Section ID:** `GOALS`

**DP030-GOALS-001**
- Preserve the domain architecture and authority boundaries defined by this proposal.
**DP030-GOALS-002**
- Make the proposal consumable by incremental functional-set Planning.
**DP030-GOALS-003**
- Keep Design statement identity distinct from repository normative identity.

## Non-Goals

**Section ID:** `NON-GOALS`

**DP030-NON-GOALS-001**
- Define one complete implementation plan for the entire proposal.
**DP030-NON-GOALS-002**
- Assign repository normative IDs during Design.
**DP030-NON-GOALS-003**
- Define file-level pseudo-code in Design unless it is itself a semantic constraint.

## Requirements

**Section ID:** `REQUIREMENTS`

**DP030-REQUIREMENTS-001**
The detailed Design below contains addressable Design statements. Statement IDs are non-normative proposal references. `functional-set.json` selects them; `plan.json` owns decomposition and normative distillation.

## Constraints

**Section ID:** `CONSTRAINTS`

**DP030-CONSTRAINTS-001**
This proposal remains subordinate to its declared Design dependencies and shall not silently assume authority outside them.

## Architecture

**Section ID:** `ARCHITECTURE`

**DP030-ARCHITECTURE-001**
The detailed Design below is semantic input to Planning and may be realized over multiple functional sets.

## Behavior

**Section ID:** `BEHAVIOR`

**DP030-BEHAVIOR-001**
Planning may consume a bounded subset of this proposal in one functional set; implementation of the entire proposal in one pass is not required.

## Interfaces and Boundaries

**Section ID:** `INTERFACES-AND-BOUNDARIES`

**DP030-INTERFACES-AND-BOUNDARIES-001**
Design defines meaning. `functional-set.json` defines selected Design scope. `plan.json` defines normative decomposition and exact implementation intent. Build produces syntactically correct, validated, operational code.

## Invariants

**Section ID:** `INVARIANTS`

**DP030-INVARIANTS-001**
- Design statement IDs remain non-normative.
**DP030-INVARIANTS-002**
- Planning owns normative distillation and implementation intent.
**DP030-INVARIANTS-003**
- Build shall not invent missing Design semantics or missing Plan intent.

## Alternatives Considered

**Section ID:** `ALTERNATIVES-CONSIDERED`

**DP030-ALTERNATIVES-CONSIDERED-001**
Domain-specific alternatives remain in the detailed Design. The revised workflow rejects collapsing Design, Planning, and Build into one artifact or stage.

## Risks and Tradeoffs

**Section ID:** `RISKS-AND-TRADEOFFS`

**DP030-RISKS-AND-TRADEOFFS-001**
Incremental realization may expose missing or ambiguous Design later; those defects must route to Design rather than being silently invented during Planning or Build.

## Open Questions

**Section ID:** `OPEN-QUESTIONS`

**DP030-OPEN-QUESTIONS-001**
No blocking workflow-format questions remain. Domain-specific open questions are retained in the detailed Design.

## Acceptance Criteria

**Section ID:** `ACCEPTANCE-CRITERIA`

**DP030-ACCEPTANCE-CRITERIA-001**
This proposal is planning-ready when its required sections are complete, its detailed semantics remain coherent with declared dependencies, and its Design statements are addressable.

# Detailed Design

## Framework Contract Basis

**Section ID:** `FRAMEWORK-CONTRACT-BASIS`

**DP030-FRAMEWORK-CONTRACT-BASIS-001**
This proposal assumes the candidate Framework Contract requirements:

**DP030-FRAMEWORK-CONTRACT-BASIS-002**
- FC-01 — Framework Authority Location
**DP030-FRAMEWORK-CONTRACT-BASIS-003**
- FC-02 — Framework Contract Role
**DP030-FRAMEWORK-CONTRACT-BASIS-004**
- FC-03 — Keystone Set
**DP030-FRAMEWORK-CONTRACT-BASIS-005**
- FC-04 — Delegated Authority
**DP030-FRAMEWORK-CONTRACT-BASIS-006**
- FC-05 — Governance Exclusivity
**DP030-FRAMEWORK-CONTRACT-BASIS-007**
- FC-06 — Conformance Exclusivity
**DP030-FRAMEWORK-CONTRACT-BASIS-008**
- FC-07 — Assurance Exclusivity
**DP030-FRAMEWORK-CONTRACT-BASIS-009**
- FC-08 — Assurance Persistence Boundary
**DP030-FRAMEWORK-CONTRACT-BASIS-010**
- FC-09 — Keystone Separation
**DP030-FRAMEWORK-CONTRACT-BASIS-011**
- FC-10 — Derived Provenance
**DP030-FRAMEWORK-CONTRACT-BASIS-012**
- FC-11 — No Implicit Authority
**DP030-FRAMEWORK-CONTRACT-BASIS-013**
- FC-12 — Product Subordination
**DP030-FRAMEWORK-CONTRACT-BASIS-014**
- FC-13 — Authority Identity
**DP030-FRAMEWORK-CONTRACT-BASIS-015**
- FC-14 — Delegation Resolution

**DP030-FRAMEWORK-CONTRACT-BASIS-016**
Conformance shall not assume authority beyond that delegated by the Framework Contract.

## Governance Basis

**Section ID:** `GOVERNANCE-BASIS`

**DP030-GOVERNANCE-BASIS-001**
This proposal assumes the candidate Governance lifecycle:

**DP030-GOVERNANCE-BASIS-002**
**Design Proposal**
**DP030-GOVERNANCE-BASIS-003**
→ **Design**
**DP030-GOVERNANCE-BASIS-004**
→ **Plan**
**DP030-GOVERNANCE-BASIS-005**
→ **Build**

**DP030-GOVERNANCE-BASIS-006**
Design produces planning-ready Markdown Design Proposals.

**DP030-GOVERNANCE-BASIS-007**
Planning selects one bounded functional set and produces a durable Plan containing normative distillation and exact implementation intent.

**DP030-GOVERNANCE-BASIS-008**
Build produces syntactically correct, validated, operational source from the accepted Plan.

**DP030-GOVERNANCE-BASIS-009**
Conformance may provide mechanical findings and evidence to Governance.

**DP030-GOVERNANCE-BASIS-010**
Conformance shall not create Governance authority or constitute Governance acceptance.

## Objective

**Section ID:** `OBJECTIVE`

**DP030-OBJECTIVE-001**
Conformance shall provide one closed mechanical-enforcement architecture in which:

**DP030-OBJECTIVE-002**
- every maintained Conformance primitive derives from accepted normative authority;
**DP030-OBJECTIVE-003**
- every mechanically applicable accepted requirement resolves to executable enforcement;
**DP030-OBJECTIVE-004**
- every executable assertion has required evidence;
**DP030-OBJECTIVE-005**
- every gating assertion participates in authorized canonical execution; and
**DP030-OBJECTIVE-006**
- no Conformance primitive or finding independently creates normative semantics.

**DP030-OBJECTIVE-007**
The primary relationship is:

**DP030-OBJECTIVE-008**
**accepted normative requirement**
**DP030-OBJECTIVE-009**
↔ **canonical Conformance correspondence**
**DP030-OBJECTIVE-010**
↔ **Conformance primitive graph**
**DP030-OBJECTIVE-011**
↔ **mechanical findings and evidence**

**DP030-OBJECTIVE-012**
The architecture shall establish four closure properties:

**DP030-OBJECTIVE-013**
1. authority closure;
**DP030-OBJECTIVE-014**
2. coverage closure;
**DP030-OBJECTIVE-015**
3. evidence closure; and
**DP030-OBJECTIVE-016**
4. execution closure.

## Conformance Boundary

**Section ID:** `CONFORMANCE-BOUNDARY`

**DP030-CONFORMANCE-BOUNDARY-001**
Conformance owns mechanical evaluation of objectively decidable obligations derived from accepted normative authority.

**DP030-CONFORMANCE-BOUNDARY-002**
Conformance may:

**DP030-CONFORMANCE-BOUNDARY-003**
- inspect observable state;
**DP030-CONFORMANCE-BOUNDARY-004**
- evaluate mechanical predicates;
**DP030-CONFORMANCE-BOUNDARY-005**
- reject mechanically nonconforming state;
**DP030-CONFORMANCE-BOUNDARY-006**
- produce mechanical findings;
**DP030-CONFORMANCE-BOUNDARY-007**
- produce deterministic evidence;
**DP030-CONFORMANCE-BOUNDARY-008**
- maintain canonical Conformance correspondence;
**DP030-CONFORMANCE-BOUNDARY-009**
- maintain Conformance primitives;
**DP030-CONFORMANCE-BOUNDARY-010**
- maintain canonical execution surfaces;
**DP030-CONFORMANCE-BOUNDARY-011**
- mechanically verify its own closure properties; and
**DP030-CONFORMANCE-BOUNDARY-012**
- expose subordinate generated views.

**DP030-CONFORMANCE-BOUNDARY-013**
Conformance shall not:

**DP030-CONFORMANCE-BOUNDARY-014**
- create normative requirements;
**DP030-CONFORMANCE-BOUNDARY-015**
- amend normative requirements;
**DP030-CONFORMANCE-BOUNDARY-016**
- extend accepted normative semantics;
**DP030-CONFORMANCE-BOUNDARY-017**
- choose among materially ambiguous interpretations;
**DP030-CONFORMANCE-BOUNDARY-018**
- convert implementation preference into normative enforcement;
**DP030-CONFORMANCE-BOUNDARY-019**
- infer normative authority from historical behavior;
**DP030-CONFORMANCE-BOUNDARY-020**
- treat implementation as normative authority;
**DP030-CONFORMANCE-BOUNDARY-021**
- perform semantic adjudication reserved to Assurance; or
**DP030-CONFORMANCE-BOUNDARY-022**
- establish Governance acceptance.

## Conformance Terminology

**Section ID:** `CONFORMANCE-TERMINOLOGY`

### Normative Requirement

**Section ID:** `NORMATIVE-REQUIREMENT`

**DP030-NORMATIVE-REQUIREMENT-001**
An identified accepted normative obligation.

**DP030-NORMATIVE-REQUIREMENT-002**
The normative requirement is the semantic authority.

**DP030-NORMATIVE-REQUIREMENT-003**
Conformance references the requirement but shall not independently restate, replace, or extend its semantics.

### Conformance Correspondence

**Section ID:** `CONFORMANCE-CORRESPONDENCE`

**DP030-CONFORMANCE-CORRESPONDENCE-001**
The governed relationship between one accepted normative requirement and the Conformance responsibility derived from that requirement.

**DP030-CONFORMANCE-CORRESPONDENCE-002**
Correspondence records:

**DP030-CONFORMANCE-CORRESPONDENCE-003**
- requirement identity;
**DP030-CONFORMANCE-CORRESPONDENCE-004**
- Conformance applicability; and
**DP030-CONFORMANCE-CORRESPONDENCE-005**
- direct assertion relationships where applicable.

**DP030-CONFORMANCE-CORRESPONDENCE-006**
Correspondence does not independently own normative semantics.

### Conformance Primitive

**Section ID:** `CONFORMANCE-PRIMITIVE`

**DP030-CONFORMANCE-PRIMITIVE-001**
A maintained executable, declarative, evidentiary, supporting, or orchestration element whose purpose participates in normative mechanical enforcement.

### Assertion

**Section ID:** `ASSERTION`

**DP030-ASSERTION-001**
A Conformance primitive representing one independently identifiable mechanically decidable predicate derived from accepted normative authority.

**DP030-ASSERTION-002**
An assertion is the primary executable unit of mechanical enforcement correspondence.

### Evidence Primitive

**Section ID:** `EVIDENCE-PRIMITIVE`

**DP030-EVIDENCE-PRIMITIVE-001**
A Conformance primitive whose purpose is to demonstrate the behavior of an assertion or enforcement path.

### Supporting Primitive

**Section ID:** `SUPPORTING-PRIMITIVE`

**DP030-SUPPORTING-PRIMITIVE-001**
A Conformance primitive that supports enforcement without itself representing a complete normative predicate.

### Orchestration Primitive

**Section ID:** `ORCHESTRATION-PRIMITIVE`

**DP030-ORCHESTRATION-PRIMITIVE-001**
A Conformance primitive responsible for composing, discovering, dispatching, loading, or executing other Conformance primitives.

## Closed Conformance Hierarchy

**Section ID:** `CLOSED-CONFORMANCE-HIERARCHY`

**DP030-CLOSED-CONFORMANCE-HIERARCHY-001**
Normative mechanical enforcement shall occur only through the governed Conformance hierarchy.

**DP030-CLOSED-CONFORMANCE-HIERARCHY-002**
A maintained artifact whose purpose is normative mechanical enforcement shall participate in that hierarchy.

**DP030-CLOSED-CONFORMANCE-HIERARCHY-003**
Applicable artifacts include:

**DP030-CLOSED-CONFORMANCE-HIERARCHY-004**
- assertions;
**DP030-CLOSED-CONFORMANCE-HIERARCHY-005**
- schemas;
**DP030-CLOSED-CONFORMANCE-HIERARCHY-006**
- helpers;
**DP030-CLOSED-CONFORMANCE-HIERARCHY-007**
- adapters;
**DP030-CLOSED-CONFORMANCE-HIERARCHY-008**
- fixtures;
**DP030-CLOSED-CONFORMANCE-HIERARCHY-009**
- tests;
**DP030-CLOSED-CONFORMANCE-HIERARCHY-010**
- runners;
**DP030-CLOSED-CONFORMANCE-HIERARCHY-011**
- dispatchers;
**DP030-CLOSED-CONFORMANCE-HIERARCHY-012**
- loaders;
**DP030-CLOSED-CONFORMANCE-HIERARCHY-013**
- registries;
**DP030-CLOSED-CONFORMANCE-HIERARCHY-014**
- generators; and
**DP030-CLOSED-CONFORMANCE-HIERARCHY-015**
- other enforcement-supporting artifacts.

**DP030-CLOSED-CONFORMANCE-HIERARCHY-016**
An artifact outside the governed Conformance hierarchy shall not independently impose normative mechanical enforcement.

**DP030-CLOSED-CONFORMANCE-HIERARCHY-017**
Conformance may consume general implementation outside the hierarchy.

**DP030-CLOSED-CONFORMANCE-HIERARCHY-018**
Such implementation does not become normative authority merely because Conformance depends on it.

## Purpose of the Closed Hierarchy

**Section ID:** `PURPOSE-OF-THE-CLOSED-HIERARCHY`

**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-001**
The closed hierarchy is an authority-control mechanism rather than merely a directory convention.

**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-002**
It prevents:

**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-003**
- ad hoc validation;
**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-004**
- hidden enforcement in unrelated implementation;
**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-005**
- ungoverned AI-generated validators;
**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-006**
- orphan tests;
**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-007**
- orphan fixtures;
**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-008**
- helpers that silently introduce constraints;
**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-009**
- schemas that become de facto semantic authorities;
**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-010**
- duplicate requirement-to-validator registries; and
**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-011**
- enforcement derived from historical implementation rather than accepted authority.

**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-012**
When mechanical enforcement is required, the governed relationship is:

**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-013**
**accepted normative requirement**
**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-014**
→ **canonical Conformance correspondence**
**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-015**
→ **assertion**
**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-016**
→ **supporting and evidence primitives**
**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-017**
→ **canonical execution**

**DP030-PURPOSE-OF-THE-CLOSED-HIERARCHY-018**
If no accepted normative requirement authorizes an enforcement behavior, Conformance shall not invent that behavior.

## Primitive Classes

**Section ID:** `PRIMITIVE-CLASSES`

**DP030-PRIMITIVE-CLASSES-001**
Conformance shall distinguish at least four functional primitive classes:

**DP030-PRIMITIVE-CLASSES-002**
1. assertions;
**DP030-PRIMITIVE-CLASSES-003**
2. supporting primitives;
**DP030-PRIMITIVE-CLASSES-004**
3. evidence primitives; and
**DP030-PRIMITIVE-CLASSES-005**
4. orchestration primitives.

**DP030-PRIMITIVE-CLASSES-006**
A subordinate controlled taxonomy may further distinguish:

**DP030-PRIMITIVE-CLASSES-007**
- helper;
**DP030-PRIMITIVE-CLASSES-008**
- adapter;
**DP030-PRIMITIVE-CLASSES-009**
- schema;
**DP030-PRIMITIVE-CLASSES-010**
- fixture;
**DP030-PRIMITIVE-CLASSES-011**
- positive case;
**DP030-PRIMITIVE-CLASSES-012**
- rejection case;
**DP030-PRIMITIVE-CLASSES-013**
- boundary case;
**DP030-PRIMITIVE-CLASSES-014**
- regression case;
**DP030-PRIMITIVE-CLASSES-015**
- mutation case;
**DP030-PRIMITIVE-CLASSES-016**
- unit test;
**DP030-PRIMITIVE-CLASSES-017**
- integration test;
**DP030-PRIMITIVE-CLASSES-018**
- self-test;
**DP030-PRIMITIVE-CLASSES-019**
- runner;
**DP030-PRIMITIVE-CLASSES-020**
- dispatcher;
**DP030-PRIMITIVE-CLASSES-021**
- loader;
**DP030-PRIMITIVE-CLASSES-022**
- registry; and
**DP030-PRIMITIVE-CLASSES-023**
- generator.

**DP030-PRIMITIVE-CLASSES-024**
Primitive class identifies Conformance role.

**DP030-PRIMITIVE-CLASSES-025**
Primitive class does not grant normative authority.

## Assertion Model

**Section ID:** `ASSERTION-MODEL`

**DP030-ASSERTION-MODEL-001**
An assertion represents one independently identifiable mechanically decidable predicate.

**DP030-ASSERTION-MODEL-002**
Assertion identity shall be distinct from implementation-callable identity.

**DP030-ASSERTION-MODEL-003**
One normative requirement may derive multiple assertions.

**DP030-ASSERTION-MODEL-004**
Multiple assertions may share one callable where their identities and provenance remain distinguishable.

**DP030-ASSERTION-MODEL-005**
For example:

**DP030-ASSERTION-MODEL-006**
**Requirement R**
**DP030-ASSERTION-MODEL-007**
→ **Assertion A1**
**DP030-ASSERTION-MODEL-008**
→ callable X

**DP030-ASSERTION-MODEL-009**
**Requirement R**
**DP030-ASSERTION-MODEL-010**
→ **Assertion A2**
**DP030-ASSERTION-MODEL-011**
→ callable X

**DP030-ASSERTION-MODEL-012**
The callable is implementation.

**DP030-ASSERTION-MODEL-013**
A1 and A2 are independently identifiable enforcement predicates.

**DP030-ASSERTION-MODEL-014**
This permits precise correspondence without requiring one trivial implementation function per assertion.

## Assertion Ownership

**Section ID:** `ASSERTION-OWNERSHIP`

**DP030-ASSERTION-OWNERSHIP-001**
Each assertion shall directly resolve to exactly one accepted normative requirement.

**DP030-ASSERTION-OWNERSHIP-002**
If one implementation callable checks predicates derived from multiple requirements, separate assertion identities shall represent those predicates.

**DP030-ASSERTION-OWNERSHIP-003**
This preserves deterministic semantic ownership while permitting shared implementation.

## Supporting Primitive Sharing

**Section ID:** `SUPPORTING-PRIMITIVE-SHARING`

**DP030-SUPPORTING-PRIMITIVE-SHARING-001**
Supporting primitives may serve multiple assertions.

**DP030-SUPPORTING-PRIMITIVE-SHARING-002**
A shared primitive does not require one direct normative owner when its transitive provenance remains resolvable.

**DP030-SUPPORTING-PRIMITIVE-SHARING-003**
Examples include:

**DP030-SUPPORTING-PRIMITIVE-SHARING-004**
- helper libraries;
**DP030-SUPPORTING-PRIMITIVE-SHARING-005**
- parsers;
**DP030-SUPPORTING-PRIMITIVE-SHARING-006**
- adapters;
**DP030-SUPPORTING-PRIMITIVE-SHARING-007**
- shared fixtures;
**DP030-SUPPORTING-PRIMITIVE-SHARING-008**
- common runners; and
**DP030-SUPPORTING-PRIMITIVE-SHARING-009**
- common infrastructure.

**DP030-SUPPORTING-PRIMITIVE-SHARING-010**
Shared support shall not be duplicated merely to create artificial one-requirement-per-function correspondence.

## Direct and Transitive Provenance

**Section ID:** `DIRECT-AND-TRANSITIVE-PROVENANCE`

**DP030-DIRECT-AND-TRANSITIVE-PROVENANCE-001**
Conformance shall distinguish direct provenance from transitive provenance.

### Direct Provenance

**Section ID:** `DIRECT-PROVENANCE`

**DP030-DIRECT-PROVENANCE-001**
A primitive directly corresponds to a requirement-derived enforcement or evidence obligation.

**DP030-DIRECT-PROVENANCE-002**
Typical examples include:

**DP030-DIRECT-PROVENANCE-003**
- assertion;
**DP030-DIRECT-PROVENANCE-004**
- requirement-specific rejection case;
**DP030-DIRECT-PROVENANCE-005**
- requirement-specific boundary case; and
**DP030-DIRECT-PROVENANCE-006**
- requirement-specific fixture.

### Transitive Provenance

**Section ID:** `TRANSITIVE-PROVENANCE`

**DP030-TRANSITIVE-PROVENANCE-001**
A primitive supports another Conformance primitive that ultimately resolves to accepted normative authority.

**DP030-TRANSITIVE-PROVENANCE-002**
Typical examples include:

**DP030-TRANSITIVE-PROVENANCE-003**
- shared helper;
**DP030-TRANSITIVE-PROVENANCE-004**
- parser;
**DP030-TRANSITIVE-PROVENANCE-005**
- adapter;
**DP030-TRANSITIVE-PROVENANCE-006**
- runner;
**DP030-TRANSITIVE-PROVENANCE-007**
- loader; and
**DP030-TRANSITIVE-PROVENANCE-008**
- common fixture.

**DP030-TRANSITIVE-PROVENANCE-009**
Both relationships shall be mechanically resolvable.

## Authority Closure

**Section ID:** `AUTHORITY-CLOSURE`

**DP030-AUTHORITY-CLOSURE-001**
Every maintained Conformance primitive shall resolve through governed provenance to at least one accepted normative requirement.

**DP030-AUTHORITY-CLOSURE-002**
Conceptually:

**DP030-AUTHORITY-CLOSURE-003**
**∀ maintained primitive P: ∃ accepted requirement R such that R →* P**

**DP030-AUTHORITY-CLOSURE-004**
No orphan Conformance primitive is permitted.

**DP030-AUTHORITY-CLOSURE-005**
An orphan primitive is a Conformance defect.

**DP030-AUTHORITY-CLOSURE-006**
Normative provenance shall not be inferred solely from:

**DP030-AUTHORITY-CLOSURE-007**
- file location;
**DP030-AUTHORITY-CLOSURE-008**
- naming;
**DP030-AUTHORITY-CLOSURE-009**
- nearby tests;
**DP030-AUTHORITY-CLOSURE-010**
- implementation behavior;
**DP030-AUTHORITY-CLOSURE-011**
- historical use; or
**DP030-AUTHORITY-CLOSURE-012**
- apparent usefulness.

## Canonical Correspondence

**Section ID:** `CANONICAL-CORRESPONDENCE`

**DP030-CANONICAL-CORRESPONDENCE-001**
Each active normative requirement shall have exactly one canonical Conformance correspondence record.

**DP030-CANONICAL-CORRESPONDENCE-002**
The correspondence record shall identify:

**DP030-CANONICAL-CORRESPONDENCE-003**
- the normative requirement;
**DP030-CANONICAL-CORRESPONDENCE-004**
- its canonical Conformance applicability; and
**DP030-CANONICAL-CORRESPONDENCE-005**
- its direct assertion relationships where applicable.

**DP030-CANONICAL-CORRESPONDENCE-006**
If Conformance applicability is `none`, the correspondence shall identify the governed rationale for that determination.

**DP030-CANONICAL-CORRESPONDENCE-007**
Correspondence shall not duplicate normative requirement text as independent semantic authority.

## Conformance Applicability

**Section ID:** `CONFORMANCE-APPLICABILITY`

**DP030-CONFORMANCE-APPLICABILITY-001**
Each active normative requirement shall have exactly one canonical Conformance applicability determination.

**DP030-CONFORMANCE-APPLICABILITY-002**
The candidate vocabulary is:

### `mechanical`

**Section ID:** `MECHANICAL`

**DP030-MECHANICAL-001**
The requirement has mechanically enforceable responsibility within Conformance scope.

**DP030-MECHANICAL-002**
A mechanically applicable requirement shall resolve to executable assertion coverage.

### `none`

**Section ID:** `NONE`

**DP030-NONE-001**
The requirement has no meaningful mechanical enforcement responsibility within Conformance scope.

**DP030-NONE-002**
A governed rationale is required.

**DP030-NONE-003**
Conformance applicability describes only Conformance responsibility.

**DP030-NONE-004**
It shall not encode Assurance responsibility.

**DP030-NONE-005**
Terms such as:

**DP030-NONE-006**
- `partial`; and
**DP030-NONE-007**
- `semantic-review`

**DP030-NONE-008**
shall therefore not be primary Conformance dispositions.

**DP030-NONE-009**
A requirement may independently have:

**DP030-NONE-010**
- mechanical Conformance responsibility; and
**DP030-NONE-011**
- Assurance responsibility.

**DP030-NONE-012**
Cross-keystone conditions should be derived from those separate relationships.

## Requirement Quality and Mechanical Decomposition

**Section ID:** `REQUIREMENT-QUALITY-AND-MECHANICAL-DECOM`

**DP030-REQUIREMENT-QUALITY-AND-MECHANICAL-DECOM-001**
Conformance shall not silently decompose ambiguous normative authority into invented normative predicates.

**DP030-REQUIREMENT-QUALITY-AND-MECHANICAL-DECOM-002**
If selected Design contains multiple independently governed obligations, Planning should distill those obligations into appropriate repository normative requirements.

**DP030-REQUIREMENT-QUALITY-AND-MECHANICAL-DECOM-003**
If an assertion requires choosing among materially different semantic interpretations, Conformance shall not make that choice independently.

**DP030-REQUIREMENT-QUALITY-AND-MECHANICAL-DECOM-004**
The issue shall route through Governance and, where semantic judgment is required, Assurance.

**DP030-REQUIREMENT-QUALITY-AND-MECHANICAL-DECOM-005**
Conformance shall not alter normative meaning merely to make enforcement easier to implement.

## Coverage Closure

**Section ID:** `COVERAGE-CLOSURE`

**DP030-COVERAGE-CLOSURE-001**
Each accepted normative requirement with mechanical Conformance applicability shall resolve to at least one executable assertion.

**DP030-COVERAGE-CLOSURE-002**
Conceptually:

**DP030-COVERAGE-CLOSURE-003**
**∀ mechanical requirement R: ∃ executable assertion A such that R → A**

**DP030-COVERAGE-CLOSURE-004**
A mechanical applicability determination with zero executable assertions is incomplete Conformance.

**DP030-COVERAGE-CLOSURE-005**
Correspondence metadata alone does not satisfy coverage closure.

## Evidence Model

**Section ID:** `EVIDENCE-MODEL`

**DP030-EVIDENCE-MODEL-001**
Executable enforcement requires governed evidence demonstrating that enforcement behaves correctly.

**DP030-EVIDENCE-MODEL-002**
Evidence classes may include:

**DP030-EVIDENCE-MODEL-003**
- rejection evidence;
**DP030-EVIDENCE-MODEL-004**
- positive evidence;
**DP030-EVIDENCE-MODEL-005**
- boundary evidence;
**DP030-EVIDENCE-MODEL-006**
- regression evidence;
**DP030-EVIDENCE-MODEL-007**
- mutation evidence;
**DP030-EVIDENCE-MODEL-008**
- unit evidence;
**DP030-EVIDENCE-MODEL-009**
- integration evidence; and
**DP030-EVIDENCE-MODEL-010**
- self-test evidence.

**DP030-EVIDENCE-MODEL-011**
The exact evidence obligations applicable to an assertion belong in subordinate Conformance authority.

## Evidence Closure

**Section ID:** `EVIDENCE-CLOSURE`

**DP030-EVIDENCE-CLOSURE-001**
Each executable assertion shall satisfy the governed evidence obligations applicable to that assertion.

**DP030-EVIDENCE-CLOSURE-002**
Conceptually:

**DP030-EVIDENCE-CLOSURE-003**
**∀ executable assertion A: required evidence obligations(A) are satisfied**

**DP030-EVIDENCE-CLOSURE-004**
Evidence should be sufficient to demonstrate that the assertion behaves as intended as mechanical enforcement.

**DP030-EVIDENCE-CLOSURE-005**
An assertion shall not be considered adequately evidenced merely because its implementation executes successfully.

## Rejection Evidence

**Section ID:** `REJECTION-EVIDENCE`

**DP030-REJECTION-EVIDENCE-001**
Rejection evidence demonstrates that representative violating state is rejected.

**DP030-REJECTION-EVIDENCE-002**
Rejection evidence is the expected baseline for most enforcement assertions because it demonstrates that the targeted violation changes the Conformance result.

**DP030-REJECTION-EVIDENCE-003**
The exact exceptions and required rejection-evidence rules belong in subordinate Conformance authority.

## Positive Evidence

**Section ID:** `POSITIVE-EVIDENCE`

**DP030-POSITIVE-EVIDENCE-001**
Positive evidence demonstrates that representative conforming state is accepted.

**DP030-POSITIVE-EVIDENCE-002**
It primarily protects against over-enforcement.

**DP030-POSITIVE-EVIDENCE-003**
Positive evidence is especially useful for:

**DP030-POSITIVE-EVIDENCE-004**
- permitted alternatives;
**DP030-POSITIVE-EVIDENCE-005**
- optional structures;
**DP030-POSITIVE-EVIDENCE-006**
- extension points;
**DP030-POSITIVE-EVIDENCE-007**
- valid namespace locations; and
**DP030-POSITIVE-EVIDENCE-008**
- permitted lifecycle transitions.

## Boundary Evidence

**Section ID:** `BOUNDARY-EVIDENCE`

**DP030-BOUNDARY-EVIDENCE-001**
Boundary evidence demonstrates behavior at transitions between permitted and prohibited state.

**DP030-BOUNDARY-EVIDENCE-002**
It is especially useful for:

**DP030-BOUNDARY-EVIDENCE-003**
- cardinality;
**DP030-BOUNDARY-EVIDENCE-004**
- path roots;
**DP030-BOUNDARY-EVIDENCE-005**
- namespaces;
**DP030-BOUNDARY-EVIDENCE-006**
- lifecycle transitions;
**DP030-BOUNDARY-EVIDENCE-007**
- exact sets;
**DP030-BOUNDARY-EVIDENCE-008**
- optional versus required structures; and
**DP030-BOUNDARY-EVIDENCE-009**
- minimum or maximum values.

## Regression Evidence

**Section ID:** `REGRESSION-EVIDENCE`

**DP030-REGRESSION-EVIDENCE-001**
Regression evidence demonstrates continued protection against a previously observed defect.

**DP030-REGRESSION-EVIDENCE-002**
Historical issue, defect, or revision references may accompany regression evidence.

**DP030-REGRESSION-EVIDENCE-003**
Historical provenance remains evidence only.

**DP030-REGRESSION-EVIDENCE-004**
It does not become normative authority.

## Mutation Evidence

**Section ID:** `MUTATION-EVIDENCE`

**DP030-MUTATION-EVIDENCE-001**
Mutation evidence intentionally alters otherwise conforming state to create a targeted violation.

**DP030-MUTATION-EVIDENCE-002**
Mutation evidence may demonstrate that:

**DP030-MUTATION-EVIDENCE-003**
- an assertion is actually executed;
**DP030-MUTATION-EVIDENCE-004**
- a targeted violation changes the result;
**DP030-MUTATION-EVIDENCE-005**
- canonical execution does not silently skip enforcement; and
**DP030-MUTATION-EVIDENCE-006**
- an evidence fixture meaningfully exercises the intended predicate.

**DP030-MUTATION-EVIDENCE-007**
Detailed mutation policy belongs in subordinate Conformance authority.

## Schemas

**Section ID:** `SCHEMAS`

**DP030-SCHEMAS-001**
A schema used for normative mechanical enforcement is a Conformance primitive.

**DP030-SCHEMAS-002**
Its normative provenance follows the same rule as every other Conformance primitive.

**DP030-SCHEMAS-003**
A schema does not become normative authority merely because validators consume it.

**DP030-SCHEMAS-004**
Schema behavior imposing constraints absent from accepted normative authority is over-enforcement.

**DP030-SCHEMAS-005**
Schema behavior omitting mechanically required constraints is under-enforcement.

## Fixtures

**Section ID:** `FIXTURES`

**DP030-FIXTURES-001**
A maintained fixture used by Conformance is a Conformance primitive.

**DP030-FIXTURES-002**
Its provenance shall resolve directly or transitively to the enforcement or evidence responsibility it serves.

**DP030-FIXTURES-003**
Fixture meaning shall not depend solely on file naming or directory placement.

**DP030-FIXTURES-004**
Where fixture role affects Conformance behavior, that role should be mechanically resolvable.

## Unit Tests

**Section ID:** `UNIT-TESTS`

**DP030-UNIT-TESTS-001**
A maintained unit test of Conformance implementation is a Conformance primitive.

**DP030-UNIT-TESTS-002**
It shall resolve to the primitive or responsibility whose behavior it verifies.

**DP030-UNIT-TESTS-003**
Through that relationship it shall resolve to accepted normative authority.

**DP030-UNIT-TESTS-004**
Unit tests demonstrate implementation behavior.

**DP030-UNIT-TESTS-005**
They do not by themselves satisfy coverage closure unless they also represent identified executable assertions.

## Integration Tests

**Section ID:** `INTEGRATION-TESTS`

**DP030-INTEGRATION-TESTS-001**
An integration test is a Conformance evidence primitive that verifies behavior through maintained execution boundaries.

**DP030-INTEGRATION-TESTS-002**
It may verify:

**DP030-INTEGRATION-TESTS-003**
- runner composition;
**DP030-INTEGRATION-TESTS-004**
- dispatch;
**DP030-INTEGRATION-TESTS-005**
- public validation surfaces;
**DP030-INTEGRATION-TESTS-006**
- failure propagation; and
**DP030-INTEGRATION-TESTS-007**
- repository-wide execution.

**DP030-INTEGRATION-TESTS-008**
Integration evidence remains subordinate to accepted normative authority.

## Self-Tests

**Section ID:** `SELF-TESTS`

**DP030-SELF-TESTS-001**
Conformance self-tests verify the Conformance architecture and implementation itself.

**DP030-SELF-TESTS-002**
Self-tests may verify:

**DP030-SELF-TESTS-003**
- provenance closure;
**DP030-SELF-TESTS-004**
- correspondence integrity;
**DP030-SELF-TESTS-005**
- assertion execution;
**DP030-SELF-TESTS-006**
- evidence relationships;
**DP030-SELF-TESTS-007**
- canonical execution;
**DP030-SELF-TESTS-008**
- schema behavior;
**DP030-SELF-TESTS-009**
- runner behavior;
**DP030-SELF-TESTS-010**
- generated projections; and
**DP030-SELF-TESTS-011**
- failure propagation.

**DP030-SELF-TESTS-012**
Self-tests are themselves Conformance primitives.

**DP030-SELF-TESTS-013**
They shall satisfy the same provenance obligations as other maintained Conformance primitives.

**DP030-SELF-TESTS-014**
Conformance shall not exempt its own infrastructure from its authority model.

## Orchestration Primitives

**Section ID:** `ORCHESTRATION-PRIMITIVES`

**DP030-ORCHESTRATION-PRIMITIVES-001**
Runners, dispatchers, loaders, registries, and similar orchestration mechanisms are Conformance primitives.

**DP030-ORCHESTRATION-PRIMITIVES-002**
Their provenance may be transitive through the assertions and Conformance responsibilities they serve.

**DP030-ORCHESTRATION-PRIMITIVES-003**
They do not need to claim direct ownership of every normative requirement whose enforcement they orchestrate.

## Canonical Execution

**Section ID:** `CANONICAL-EXECUTION`

**DP030-CANONICAL-EXECUTION-001**
Conformance shall define authorized canonical execution surfaces.

**DP030-CANONICAL-EXECUTION-002**
Each gating assertion shall be reachable from an authorized canonical Conformance execution surface.

**DP030-CANONICAL-EXECUTION-003**
Canonical execution may be hierarchical.

**DP030-CANONICAL-EXECUTION-004**
For example:

**DP030-CANONICAL-EXECUTION-005**
**repository Conformance runner**
**DP030-CANONICAL-EXECUTION-006**
→ **framework Conformance runner**
**DP030-CANONICAL-EXECUTION-007**
→ **product Conformance runner**

**DP030-CANONICAL-EXECUTION-008**
The exact orchestration model belongs in subordinate design.

## Execution Closure

**Section ID:** `EXECUTION-CLOSURE`

**DP030-EXECUTION-CLOSURE-001**
Each gating assertion shall participate in authorized canonical execution.

**DP030-EXECUTION-CLOSURE-002**
Conceptually:

**DP030-EXECUTION-CLOSURE-003**
**∀ gating assertion A: canonical execution →* A**

**DP030-EXECUTION-CLOSURE-004**
An assertion may have correct authority, correspondence, and evidence while still failing to provide actual enforcement if it is not executed through the required gating path.

**DP030-EXECUTION-CLOSURE-005**
Execution closure prevents that condition.

## The Four Closure Properties

**Section ID:** `THE-FOUR-CLOSURE-PROPERTIES`

**DP030-THE-FOUR-CLOSURE-PROPERTIES-001**
The architecture centers on four closure properties.

### Authority Closure

**Section ID:** `AUTHORITY-CLOSURE`

**DP030-AUTHORITY-CLOSURE-013**
**accepted normative authority → every maintained Conformance primitive**

**DP030-AUTHORITY-CLOSURE-014**
No orphan Conformance behavior.

### Coverage Closure

**Section ID:** `COVERAGE-CLOSURE`

**DP030-COVERAGE-CLOSURE-006**
**mechanically applicable requirement → executable assertion**

**DP030-COVERAGE-CLOSURE-007**
No mechanically applicable requirement without enforcement.

### Evidence Closure

**Section ID:** `EVIDENCE-CLOSURE`

**DP030-EVIDENCE-CLOSURE-006**
**executable assertion → required evidence**

**DP030-EVIDENCE-CLOSURE-007**
No unsupported enforcement predicate.

### Execution Closure

**Section ID:** `EXECUTION-CLOSURE`

**DP030-EXECUTION-CLOSURE-006**
**authorized canonical execution → every gating assertion**

**DP030-EXECUTION-CLOSURE-007**
No required enforcement silently omitted from execution.

**DP030-EXECUTION-CLOSURE-008**
Together:

**DP030-EXECUTION-CLOSURE-009**
**Authority explains why enforcement exists.**

**DP030-EXECUTION-CLOSURE-010**
**Coverage establishes that required enforcement exists.**

**DP030-EXECUTION-CLOSURE-011**
**Evidence demonstrates that enforcement behaves correctly.**

**DP030-EXECUTION-CLOSURE-012**
**Execution establishes that required enforcement actually runs.**

## Bidirectional Correspondence

**Section ID:** `BIDIRECTIONAL-CORRESPONDENCE`

**DP030-BIDIRECTIONAL-CORRESPONDENCE-001**
Canonical Conformance correspondence and primitive provenance shall support mechanically resolvable forward and reverse navigation.

**DP030-BIDIRECTIONAL-CORRESPONDENCE-002**
Forward:

**DP030-BIDIRECTIONAL-CORRESPONDENCE-003**
**normative requirement**
**DP030-BIDIRECTIONAL-CORRESPONDENCE-004**
→ **canonical correspondence**
**DP030-BIDIRECTIONAL-CORRESPONDENCE-005**
→ **assertion**
**DP030-BIDIRECTIONAL-CORRESPONDENCE-006**
→ **evidence/supporting/orchestration primitives**

**DP030-BIDIRECTIONAL-CORRESPONDENCE-007**
Reverse:

**DP030-BIDIRECTIONAL-CORRESPONDENCE-008**
**Conformance primitive**
**DP030-BIDIRECTIONAL-CORRESPONDENCE-009**
→ **provenance path**
**DP030-BIDIRECTIONAL-CORRESPONDENCE-010**
→ **accepted normative requirement**

**DP030-BIDIRECTIONAL-CORRESPONDENCE-011**
Reverse provenance may be:

**DP030-BIDIRECTIONAL-CORRESPONDENCE-012**
- direct for assertions;
**DP030-BIDIRECTIONAL-CORRESPONDENCE-013**
- direct or transitive for evidence;
**DP030-BIDIRECTIONAL-CORRESPONDENCE-014**
- transitive for shared infrastructure.

## Primitive Identity

**Section ID:** `PRIMITIVE-IDENTITY`

**DP030-PRIMITIVE-IDENTITY-001**
Each Conformance primitive requiring independent correspondence shall have an identity appropriate to its governed role.

**DP030-PRIMITIVE-IDENTITY-002**
Assertion identities shall be stable and unique.

**DP030-PRIMITIVE-IDENTITY-003**
Other primitive identities shall be stable where required by correspondence, provenance, evidence, or historical resolution.

**DP030-PRIMITIVE-IDENTITY-004**
Primitive identity should remain distinct from mutable implementation coordinates where practical.

**DP030-PRIMITIVE-IDENTITY-005**
A stable primitive identity may survive:

**DP030-PRIMITIVE-IDENTITY-006**
- source movement;
**DP030-PRIMITIVE-IDENTITY-007**
- function renaming;
**DP030-PRIMITIVE-IDENTITY-008**
- helper extraction;
**DP030-PRIMITIVE-IDENTITY-009**
- runner reorganization; and
**DP030-PRIMITIVE-IDENTITY-010**
- implementation refactoring

**DP030-PRIMITIVE-IDENTITY-011**
when its governed Conformance role remains unchanged.

**DP030-PRIMITIVE-IDENTITY-012**
A Conformance primitive identity shall not be reused for unrelated behavior.

## Single Correspondence Authority

**Section ID:** `SINGLE-CORRESPONDENCE-AUTHORITY`

**DP030-SINGLE-CORRESPONDENCE-AUTHORITY-001**
Conformance shall define one canonical authority for requirement-to-Conformance correspondence.

**DP030-SINGLE-CORRESPONDENCE-AUTHORITY-002**
Independently maintained mappings shall not be allowed to silently diverge.

**DP030-SINGLE-CORRESPONDENCE-AUTHORITY-003**
Requirement relationships shall not be separately redefined without verification in:

**DP030-SINGLE-CORRESPONDENCE-AUTHORITY-004**
- correspondence records;
**DP030-SINGLE-CORRESPONDENCE-AUTHORITY-005**
- source annotations;
**DP030-SINGLE-CORRESPONDENCE-AUTHORITY-006**
- registries;
**DP030-SINGLE-CORRESPONDENCE-AUTHORITY-007**
- runner lists;
**DP030-SINGLE-CORRESPONDENCE-AUTHORITY-008**
- test manifests;
**DP030-SINGLE-CORRESPONDENCE-AUTHORITY-009**
- schemas;
**DP030-SINGLE-CORRESPONDENCE-AUTHORITY-010**
- generated documentation; or
**DP030-SINGLE-CORRESPONDENCE-AUTHORITY-011**
- dispatch logic.

**DP030-SINGLE-CORRESPONDENCE-AUTHORITY-012**
Where multiple operational representations are required, they shall be:

**DP030-SINGLE-CORRESPONDENCE-AUTHORITY-013**
- generated from canonical correspondence; or
**DP030-SINGLE-CORRESPONDENCE-AUTHORITY-014**
- mechanically verified against it.

## Correspondence Package Evolution

**Section ID:** `CORRESPONDENCE-PACKAGE-EVOLUTION`

**DP030-CORRESPONDENCE-PACKAGE-EVOLUTION-001**
The current validation-package concept may remain as the canonical requirement-level correspondence container.

**DP030-CORRESPONDENCE-PACKAGE-EVOLUTION-002**
Its role should change from a flat validation-task registry to an entry point into the Conformance graph.

**DP030-CORRESPONDENCE-PACKAGE-EVOLUTION-003**
A conceptual package may resemble:

**DP030-CORRESPONDENCE-PACKAGE-EVOLUTION-004**
{
**DP030-CORRESPONDENCE-PACKAGE-EVOLUTION-005**
  "normative_requirement_id": "REPO-VAL-021",
**DP030-CORRESPONDENCE-PACKAGE-EVOLUTION-006**
  "conformance_applicability": "mechanical",
**DP030-CORRESPONDENCE-PACKAGE-EVOLUTION-007**
  "assertions": [
**DP030-CORRESPONDENCE-PACKAGE-EVOLUTION-008**
    "CONF-ASSERT-0041",
**DP030-CORRESPONDENCE-PACKAGE-EVOLUTION-009**
    "CONF-ASSERT-0042"
**DP030-CORRESPONDENCE-PACKAGE-EVOLUTION-010**
  ]
**DP030-CORRESPONDENCE-PACKAGE-EVOLUTION-011**
}

**DP030-CORRESPONDENCE-PACKAGE-EVOLUTION-012**
The exact representation remains subject to detailed design.

**DP030-CORRESPONDENCE-PACKAGE-EVOLUTION-013**
The architectural requirement is one canonical correspondence authority, not one particular file format.

## Correspondence Integrity

**Section ID:** `CORRESPONDENCE-INTEGRITY`

**DP030-CORRESPONDENCE-INTEGRITY-001**
Canonical Conformance correspondence shall remain mechanically consistent with the maintained primitive graph.

**DP030-CORRESPONDENCE-INTEGRITY-002**
Conformance shall detect stale or contradictory relationships such as:

**DP030-CORRESPONDENCE-INTEGRITY-003**
- correspondence referencing nonexistent assertions;
**DP030-CORRESPONDENCE-INTEGRITY-004**
- assertions whose direct requirement ownership disagrees with correspondence;
**DP030-CORRESPONDENCE-INTEGRITY-005**
- removed primitives still referenced by canonical correspondence; and
**DP030-CORRESPONDENCE-INTEGRITY-006**
- duplicate operational mappings that diverge from canonical correspondence.

## Findings

**Section ID:** `FINDINGS`

**DP030-FINDINGS-001**
A Conformance finding is a mechanical result produced through governed Conformance execution.

**DP030-FINDINGS-002**
A violation finding shall identify:

**DP030-FINDINGS-003**
- the assertion from which it derives; and
**DP030-FINDINGS-004**
- the accepted normative requirement owning that assertion.

**DP030-FINDINGS-005**
A finding should additionally identify:

**DP030-FINDINGS-006**
- the observed subject;
**DP030-FINDINGS-007**
- the mechanical outcome; and
**DP030-FINDINGS-008**
- sufficient diagnostic context.

**DP030-FINDINGS-009**
Findings shall be suitable for machine resolution and human remediation.

**DP030-FINDINGS-010**
A finding shall not create, amend, or extend normative semantics.

## Finding Classes

**Section ID:** `FINDING-CLASSES`

**DP030-FINDING-CLASSES-001**
Conformance may distinguish findings such as:

**DP030-FINDING-CLASSES-002**
- pass;
**DP030-FINDING-CLASSES-003**
- violation;
**DP030-FINDING-CLASSES-004**
- Conformance-system defect; and
**DP030-FINDING-CLASSES-005**
- mechanically undecidable.

**DP030-FINDING-CLASSES-006**
`Mechanically undecidable` means Conformance cannot establish the result mechanically under current authority and implementation.

**DP030-FINDING-CLASSES-007**
It shall not be used as a substitute for Assurance judgment.

**DP030-FINDING-CLASSES-008**
If undecidability results from ambiguous authority, the issue routes toward Assurance and Governance.

**DP030-FINDING-CLASSES-009**
If undecidability results from missing or defective mechanical enforcement, it is a Conformance defect.

## Determinism

**Section ID:** `DETERMINISM`

**DP030-DETERMINISM-001**
Equivalent accepted authority and equivalent observable state should produce equivalent Conformance outcomes.

**DP030-DETERMINISM-002**
Material enforcement outcomes should not depend on incidental nondeterminism such as:

**DP030-DETERMINISM-003**
- traversal order;
**DP030-DETERMINISM-004**
- filesystem order;
**DP030-DETERMINISM-005**
- hash ordering;
**DP030-DETERMINISM-006**
- locale;
**DP030-DETERMINISM-007**
- unstable defaults; or
**DP030-DETERMINISM-008**
- irrelevant environment state.

**DP030-DETERMINISM-009**
Where external state is normatively relevant, accepted authority shall establish that relevance.

## Generated Views

**Section ID:** `GENERATED-VIEWS`

**DP030-GENERATED-VIEWS-001**
Generated Conformance coverage and correspondence views may be derived from canonical correspondence and primitive provenance.

**DP030-GENERATED-VIEWS-002**
Derived views may include:

**DP030-GENERATED-VIEWS-003**
- requirement identity;
**DP030-GENERATED-VIEWS-004**
- applicability;
**DP030-GENERATED-VIEWS-005**
- assertion relationships;
**DP030-GENERATED-VIEWS-006**
- evidence relationships;
**DP030-GENERATED-VIEWS-007**
- execution reachability;
**DP030-GENERATED-VIEWS-008**
- supporting primitives; and
**DP030-GENERATED-VIEWS-009**
- closure defects.

**DP030-GENERATED-VIEWS-010**
Generated views remain subordinate derived artifacts.

**DP030-GENERATED-VIEWS-011**
They shall not become competing correspondence or semantic authority.

**DP030-GENERATED-VIEWS-012**
A declaration such as `validated: true` shall not substitute for closure.

## Conformance Self-Validation

**Section ID:** `CONFORMANCE-SELF-VALIDATION`

**DP030-CONFORMANCE-SELF-VALIDATION-001**
Conformance shall mechanically verify the integrity of its own governed model.

**DP030-CONFORMANCE-SELF-VALIDATION-002**
At minimum, Conformance self-validation shall enforce required:

**DP030-CONFORMANCE-SELF-VALIDATION-003**
- authority closure;
**DP030-CONFORMANCE-SELF-VALIDATION-004**
- coverage closure;
**DP030-CONFORMANCE-SELF-VALIDATION-005**
- evidence closure; and
**DP030-CONFORMANCE-SELF-VALIDATION-006**
- execution closure.

**DP030-CONFORMANCE-SELF-VALIDATION-007**
It should additionally verify:

**DP030-CONFORMANCE-SELF-VALIDATION-008**
- assertion identity integrity;
**DP030-CONFORMANCE-SELF-VALIDATION-009**
- primitive identity integrity where applicable;
**DP030-CONFORMANCE-SELF-VALIDATION-010**
- correspondence integrity; and
**DP030-CONFORMANCE-SELF-VALIDATION-011**
- hierarchy integrity.

**DP030-CONFORMANCE-SELF-VALIDATION-012**
Self-validation enforces accepted Conformance authority.

**DP030-CONFORMANCE-SELF-VALIDATION-013**
It does not independently create that authority.

## Closure Enforcement

**Section ID:** `CLOSURE-ENFORCEMENT`

**DP030-CLOSURE-ENFORCEMENT-001**
A governed Conformance state that violates required closure shall be mechanically nonconforming.

**DP030-CLOSURE-ENFORCEMENT-002**
Examples include:

### Authority Closure Defect

**Section ID:** `AUTHORITY-CLOSURE-DEFECT`

**DP030-AUTHORITY-CLOSURE-DEFECT-001**
A maintained Conformance primitive has no provenance path to accepted normative authority.

### Coverage Closure Defect

**Section ID:** `COVERAGE-CLOSURE-DEFECT`

**DP030-COVERAGE-CLOSURE-DEFECT-001**
A mechanically applicable normative requirement has no executable assertion.

### Evidence Closure Defect

**Section ID:** `EVIDENCE-CLOSURE-DEFECT`

**DP030-EVIDENCE-CLOSURE-DEFECT-001**
An executable assertion does not satisfy its governed evidence obligations.

### Execution Closure Defect

**Section ID:** `EXECUTION-CLOSURE-DEFECT`

**DP030-EXECUTION-CLOSURE-DEFECT-001**
A gating assertion is unreachable from authorized canonical execution.

**DP030-EXECUTION-CLOSURE-DEFECT-002**
Conformance shall mechanically reject such states.

## Other Conformance Defects

**Section ID:** `OTHER-CONFORMANCE-DEFECTS`

**DP030-OTHER-CONFORMANCE-DEFECTS-001**
Other defects may include:

**DP030-OTHER-CONFORMANCE-DEFECTS-002**
- assertion with no direct normative owner;
**DP030-OTHER-CONFORMANCE-DEFECTS-003**
- invalid provenance edge;
**DP030-OTHER-CONFORMANCE-DEFECTS-004**
- duplicate assertion identity;
**DP030-OTHER-CONFORMANCE-DEFECTS-005**
- unrelated identity reuse;
**DP030-OTHER-CONFORMANCE-DEFECTS-006**
- stale canonical correspondence;
**DP030-OTHER-CONFORMANCE-DEFECTS-007**
- divergent duplicate mapping;
**DP030-OTHER-CONFORMANCE-DEFECTS-008**
- enforcement outside the governed hierarchy;
**DP030-OTHER-CONFORMANCE-DEFECTS-009**
- schema behavior imposing unauthorized constraints;
**DP030-OTHER-CONFORMANCE-DEFECTS-010**
- helper behavior introducing undeclared constraints;
**DP030-OTHER-CONFORMANCE-DEFECTS-011**
- finding semantics exceeding accepted authority; and
**DP030-OTHER-CONFORMANCE-DEFECTS-012**
- canonical execution silently skipping required enforcement.

**DP030-OTHER-CONFORMANCE-DEFECTS-013**
A Conformance defect shall not be repaired by inventing normative authority.

**DP030-OTHER-CONFORMANCE-DEFECTS-014**
If accepted authority is insufficient, the issue shall route through Governance and, where semantic judgment is necessary, Assurance.

## Relationship to Governance

**Section ID:** `RELATIONSHIP-TO-GOVERNANCE`

**DP030-RELATIONSHIP-TO-GOVERNANCE-001**
Governance creates and changes accepted normative authority.

**DP030-RELATIONSHIP-TO-GOVERNANCE-002**
Conformance consumes accepted normative authority.

**DP030-RELATIONSHIP-TO-GOVERNANCE-003**
Governance may require Conformance findings or evidence for stage acceptance.

**DP030-RELATIONSHIP-TO-GOVERNANCE-004**
Conformance results do not themselves constitute Governance acceptance.

**DP030-RELATIONSHIP-TO-GOVERNANCE-005**
When Conformance exposes a defect:

### Normative Semantic Defect

**Section ID:** `NORMATIVE-SEMANTIC-DEFECT`

**DP030-NORMATIVE-SEMANTIC-DEFECT-001**
Route to Governance Design.

### Realization-Intent Defect

**Section ID:** `REALIZATION-INTENT-DEFECT`

**DP030-REALIZATION-INTENT-DEFECT-001**
Route to Governance Plan.

### Realization Defect

**Section ID:** `REALIZATION-DEFECT`

**DP030-REALIZATION-DEFECT-001**
Route to Governance Build.

**DP030-REALIZATION-DEFECT-002**
Conformance reports mechanically established facts.

**DP030-REALIZATION-DEFECT-003**
Governance determines persistent change and lifecycle disposition.

## Relationship to Assurance

**Section ID:** `RELATIONSHIP-TO-ASSURANCE`

**DP030-RELATIONSHIP-TO-ASSURANCE-001**
Assurance may evaluate:

**DP030-RELATIONSHIP-TO-ASSURANCE-002**
- whether Conformance applicability is semantically justified;
**DP030-RELATIONSHIP-TO-ASSURANCE-003**
- whether an assertion correctly interprets accepted authority;
**DP030-RELATIONSHIP-TO-ASSURANCE-004**
- whether mechanical decomposition introduces unintended semantics;
**DP030-RELATIONSHIP-TO-ASSURANCE-005**
- whether evidence is semantically sufficient where mechanical criteria cannot decide sufficiency;
**DP030-RELATIONSHIP-TO-ASSURANCE-006**
- whether a requirement is too ambiguous for mechanical enforcement; and
**DP030-RELATIONSHIP-TO-ASSURANCE-007**
- whether a claimed `none` applicability is semantically justified.

**DP030-RELATIONSHIP-TO-ASSURANCE-008**
Assurance shall not independently rewrite Conformance semantics into persistent authority.

**DP030-RELATIONSHIP-TO-ASSURANCE-009**
Persistent semantic corrections shall route through Governance.

## Human and Automated Actors

**Section ID:** `HUMAN-AND-AUTOMATED-ACTORS`

**DP030-HUMAN-AND-AUTOMATED-ACTORS-001**
Humans, automated tooling, and AI agents may perform Conformance work where authorized.

**DP030-HUMAN-AND-AUTOMATED-ACTORS-002**
Actor capability does not determine authority.

**DP030-HUMAN-AND-AUTOMATED-ACTORS-003**
When adding or changing mechanical enforcement, the governed sequence should be:

**DP030-HUMAN-AND-AUTOMATED-ACTORS-004**
1. identify accepted normative authority;
**DP030-HUMAN-AND-AUTOMATED-ACTORS-005**
2. identify canonical Conformance correspondence;
**DP030-HUMAN-AND-AUTOMATED-ACTORS-006**
3. establish assertion identity;
**DP030-HUMAN-AND-AUTOMATED-ACTORS-007**
4. implement or reuse supporting primitives;
**DP030-HUMAN-AND-AUTOMATED-ACTORS-008**
5. provide required evidence;
**DP030-HUMAN-AND-AUTOMATED-ACTORS-009**
6. connect gating assertions to canonical execution;
**DP030-HUMAN-AND-AUTOMATED-ACTORS-010**
7. preserve primitive provenance; and
**DP030-HUMAN-AND-AUTOMATED-ACTORS-011**
8. verify closure.

**DP030-HUMAN-AND-AUTOMATED-ACTORS-012**
An automated actor shall not:

**DP030-HUMAN-AND-AUTOMATED-ACTORS-013**
- add ad hoc enforcement outside the hierarchy;
**DP030-HUMAN-AND-AUTOMATED-ACTORS-014**
- infer normative constraints from implementation;
**DP030-HUMAN-AND-AUTOMATED-ACTORS-015**
- invent missing requirements;
**DP030-HUMAN-AND-AUTOMATED-ACTORS-016**
- create orphan tests or fixtures;
**DP030-HUMAN-AND-AUTOMATED-ACTORS-017**
- treat schemas as independent semantic authority;
**DP030-HUMAN-AND-AUTOMATED-ACTORS-018**
- claim coverage from correspondence existence alone; or
**DP030-HUMAN-AND-AUTOMATED-ACTORS-019**
- bypass canonical execution.

## Candidate Conformance Requirements

**Section ID:** `CANDIDATE-CONFORMANCE-REQUIREMENTS`

**DP030-CANDIDATE-CONFORMANCE-REQUIREMENTS-001**
The following proposal-local statements are Design input. Their labels are non-normative; Planning may distill repository normative requirements from any combination of selected Design statements.

### CONF-01 — Closed Conformance Hierarchy

**Section ID:** `CONF-01-CLOSED-CONFORMANCE-HIERARCHY`

**DP030-CONF-01-CLOSED-CONFORMANCE-HIERARCHY-001**
**Normative mechanical enforcement SHALL occur only through the governed Conformance hierarchy.**

### CONF-02 — Primitive Provenance

**Section ID:** `CONF-02-PRIMITIVE-PROVENANCE`

**DP030-CONF-02-PRIMITIVE-PROVENANCE-001**
**Every maintained Conformance primitive SHALL resolve through governed provenance to at least one accepted normative requirement.**

### CONF-03 — Canonical Correspondence

**Section ID:** `CONF-03-CANONICAL-CORRESPONDENCE`

**DP030-CONF-03-CANONICAL-CORRESPONDENCE-001**
**Each active normative requirement SHALL have exactly one canonical Conformance correspondence record.**

### CONF-04 — Conformance Applicability

**Section ID:** `CONF-04-CONFORMANCE-APPLICABILITY`

**DP030-CONF-04-CONFORMANCE-APPLICABILITY-001**
**Each active normative requirement SHALL have exactly one canonical Conformance applicability determination.**

### CONF-05 — Mechanical Coverage

**Section ID:** `CONF-05-MECHANICAL-COVERAGE`

**DP030-CONF-05-MECHANICAL-COVERAGE-001**
**Each normative requirement with mechanical Conformance applicability SHALL resolve to at least one executable assertion.**

### CONF-06 — Assertion Identity

**Section ID:** `CONF-06-ASSERTION-IDENTITY`

**DP030-CONF-06-ASSERTION-IDENTITY-001**
**Each maintained Conformance assertion SHALL have a stable unique identity.**

### CONF-07 — Assertion Ownership

**Section ID:** `CONF-07-ASSERTION-OWNERSHIP`

**DP030-CONF-07-ASSERTION-OWNERSHIP-001**
**Each maintained Conformance assertion SHALL directly resolve to exactly one accepted normative requirement.**

### CONF-08 — Conformance Semantic Boundary

**Section ID:** `CONF-08-CONFORMANCE-SEMANTIC-BOUNDARY`

**DP030-CONF-08-CONFORMANCE-SEMANTIC-BOUNDARY-001**
**A Conformance primitive or finding SHALL NOT independently create, amend, or extend normative semantics.**

### CONF-09 — Non-Mechanical Rationale

**Section ID:** `CONF-09-NON-MECHANICAL-RATIONALE`

**DP030-CONF-09-NON-MECHANICAL-RATIONALE-001**
**A normative requirement with no mechanical Conformance applicability SHALL have a governed rationale for that determination.**

### CONF-10 — Evidence Closure

**Section ID:** `CONF-10-EVIDENCE-CLOSURE`

**DP030-CONF-10-EVIDENCE-CLOSURE-001**
**Each executable Conformance assertion SHALL satisfy the governed evidence obligations applicable to that assertion.**

### CONF-11 — Execution Closure

**Section ID:** `CONF-11-EXECUTION-CLOSURE`

**DP030-CONF-11-EXECUTION-CLOSURE-001**
**Each gating Conformance assertion SHALL be reachable from an authorized canonical Conformance execution surface.**

### CONF-12 — Correspondence Integrity

**Section ID:** `CONF-12-CORRESPONDENCE-INTEGRITY`

**DP030-CONF-12-CORRESPONDENCE-INTEGRITY-001**
**Canonical Conformance correspondence SHALL remain mechanically consistent with the maintained Conformance primitive graph.**

### CONF-13 — Single Correspondence Authority

**Section ID:** `CONF-13-SINGLE-CORRESPONDENCE-AUTHORITY`

**DP030-CONF-13-SINGLE-CORRESPONDENCE-AUTHORITY-001**
**Requirement-to-Conformance correspondence SHALL NOT depend on independently maintained mappings that may silently diverge.**

### CONF-14 — Primitive Identity Preservation

**Section ID:** `CONF-14-PRIMITIVE-IDENTITY-PRESERVATION`

**DP030-CONF-14-PRIMITIVE-IDENTITY-PRESERVATION-001**
**A Conformance primitive identity SHALL NOT be reused for unrelated Conformance behavior.**

### CONF-15 — Finding Traceability

**Section ID:** `CONF-15-FINDING-TRACEABILITY`

**DP030-CONF-15-FINDING-TRACEABILITY-001**
**A Conformance violation finding SHALL identify the assertion and accepted normative requirement from which it derives.**

### CONF-16 — Closure Enforcement

**Section ID:** `CONF-16-CLOSURE-ENFORCEMENT`

**DP030-CONF-16-CLOSURE-ENFORCEMENT-001**
**Conformance SHALL mechanically reject governed Conformance state that violates required authority, coverage, evidence, or execution closure.**

## Primary Design Invariant

**Section ID:** `PRIMARY-DESIGN-INVARIANT`

**DP030-PRIMARY-DESIGN-INVARIANT-001**
**Conformance SHALL mechanically enforce accepted normative authority through a closed and self-validating provenance graph in which every maintained Conformance primitive is authorized by accepted normative requirements, every mechanically applicable requirement resolves to executable assertions, every executable assertion satisfies required evidence obligations, every gating assertion participates in authorized canonical execution, and no Conformance primitive or finding independently creates normative semantics.**

**DP030-PRIMARY-DESIGN-INVARIANT-002**
All detailed Conformance design shall preserve this invariant.

## Audit Questions

**Section ID:** `AUDIT-QUESTIONS`

**DP030-AUDIT-QUESTIONS-001**
The current repository should be audited against this proposal by determining:

**DP030-AUDIT-QUESTIONS-002**
1. Which maintained validation artifacts are Conformance primitives.

**DP030-AUDIT-QUESTIONS-003**
2. Which current Conformance primitives lack resolvable provenance to accepted normative authority.

**DP030-AUDIT-QUESTIONS-004**
3. Which active normative requirements should have `mechanical` applicability.

**DP030-AUDIT-QUESTIONS-005**
4. Which active normative requirements should have `none` applicability.

**DP030-AUDIT-QUESTIONS-006**
5. Which current `none` or `not-applicable` decisions lack adequate rationale.

**DP030-AUDIT-QUESTIONS-007**
6. Which mechanically applicable requirements lack executable assertions.

**DP030-AUDIT-QUESTIONS-008**
7. Which current validation functions contain multiple independently identifiable assertions.

**DP030-AUDIT-QUESTIONS-009**
8. Which current tagged entry points identify implementation callables rather than independently governed assertions.

**DP030-AUDIT-QUESTIONS-010**
9. Which assertions directly map to more than one normative requirement and therefore require decomposition of assertion identity.

**DP030-AUDIT-QUESTIONS-011**
10. Which shared helpers, fixtures, schemas, runners, loaders, registries, or generators require transitive provenance.

**DP030-AUDIT-QUESTIONS-012**
11. Which unit tests, integration tests, self-tests, and other evidence primitives lack provenance.

**DP030-AUDIT-QUESTIONS-013**
12. Which executable assertions fail governed evidence obligations.

**DP030-AUDIT-QUESTIONS-014**
13. Which gating assertions are unreachable from canonical execution.

**DP030-AUDIT-QUESTIONS-015**
14. Which enforcement behavior exists outside the governed Conformance hierarchy.

**DP030-AUDIT-QUESTIONS-016**
15. Which schemas or helpers enforce constraints not clearly authorized by accepted normative authority.

**DP030-AUDIT-QUESTIONS-017**
16. Which current validation-package dispositions combine Conformance and Assurance responsibilities.

**DP030-AUDIT-QUESTIONS-018**
17. Which `partial` relationships should instead be represented by independent Conformance and Assurance correspondence.

**DP030-AUDIT-QUESTIONS-019**
18. Which `semantic-review` relationships belong entirely to Assurance.

**DP030-AUDIT-QUESTIONS-020**
19. Which validation task categories should become evidence classes rather than primary correspondence identities.

**DP030-AUDIT-QUESTIONS-021**
20. Which existing validator callables should expose multiple assertion identities.

**DP030-AUDIT-QUESTIONS-022**
21. Which current mappings are duplicated across packages, source metadata, runners, scripts, registries, or generated artifacts.

**DP030-AUDIT-QUESTIONS-023**
22. Which generated artifacts should remain subordinate projections of canonical correspondence.

**DP030-AUDIT-QUESTIONS-024**
23. Which current findings fail to identify both assertion and normative requirement identity.

**DP030-AUDIT-QUESTIONS-025**
24. Which existing self-tests already verify authority, coverage, evidence, or execution closure.

**DP030-AUDIT-QUESTIONS-026**
25. Whether each candidate CONF requirement represents one independently identifiable obligation.

**DP030-AUDIT-QUESTIONS-027**
26. Whether any candidate CONF requirement duplicates or logically follows from another.

**DP030-AUDIT-QUESTIONS-028**
27. Which candidate CONF requirements require Assurance for semantic evaluation.

**DP030-AUDIT-QUESTIONS-029**
28. What minimum Conformance authority must be accepted before Governance may require closure at Build acceptance.

## Explicitly Deferred Concerns

**Section ID:** `EXPLICITLY-DEFERRED-CONCERNS`

**DP030-EXPLICITLY-DEFERRED-CONCERNS-001**
The following concerns are intentionally outside this Conformance proposal:

**DP030-EXPLICITLY-DEFERRED-CONCERNS-002**
- exact directory layout;
**DP030-EXPLICITLY-DEFERRED-CONCERNS-003**
- exact correspondence-package schema;
**DP030-EXPLICITLY-DEFERRED-CONCERNS-004**
- exact primitive metadata syntax;
**DP030-EXPLICITLY-DEFERRED-CONCERNS-005**
- exact assertion identifier format;
**DP030-EXPLICITLY-DEFERRED-CONCERNS-006**
- exact decorator or source-tag syntax;
**DP030-EXPLICITLY-DEFERRED-CONCERNS-007**
- exact evidence-policy matrix;
**DP030-EXPLICITLY-DEFERRED-CONCERNS-008**
- exact fixture naming convention;
**DP030-EXPLICITLY-DEFERRED-CONCERNS-009**
- exact runner implementation;
**DP030-EXPLICITLY-DEFERRED-CONCERNS-010**
- exact programming language;
**DP030-EXPLICITLY-DEFERRED-CONCERNS-011**
- exact diagnostic serialization;
**DP030-EXPLICITLY-DEFERRED-CONCERNS-012**
- exact failure aggregation policy;
**DP030-EXPLICITLY-DEFERRED-CONCERNS-013**
- exact generated Markdown format;
**DP030-EXPLICITLY-DEFERRED-CONCERNS-014**
- exact mutation-testing framework;
**DP030-EXPLICITLY-DEFERRED-CONCERNS-015**
- exact Assurance correspondence model;
**DP030-EXPLICITLY-DEFERRED-CONCERNS-016**
- migration sequencing from the current validation architecture; and
**DP030-EXPLICITLY-DEFERRED-CONCERNS-017**
- bootstrap accommodations.

**DP030-EXPLICITLY-DEFERRED-CONCERNS-018**
These concerns may be defined by subordinate Conformance authority during detailed Design and Plan.

## Relationship to Assurance

**Section ID:** `RELATIONSHIP-TO-ASSURANCE`

**DP030-RELATIONSHIP-TO-ASSURANCE-010**
The Assurance Architecture Proposal shall define semantic review of:

**DP030-RELATIONSHIP-TO-ASSURANCE-011**
- normative requirement quality;
**DP030-RELATIONSHIP-TO-ASSURANCE-012**
- ambiguous or incompletely mechanical obligations;
**DP030-RELATIONSHIP-TO-ASSURANCE-013**
- Conformance applicability decisions;
**DP030-RELATIONSHIP-TO-ASSURANCE-014**
- assertion interpretation;
**DP030-RELATIONSHIP-TO-ASSURANCE-015**
- semantic sufficiency of evidence; and
**DP030-RELATIONSHIP-TO-ASSURANCE-016**
- case-specific semantic conclusions.

**DP030-RELATIONSHIP-TO-ASSURANCE-017**
Conformance shall establish mechanically decidable facts.

**DP030-RELATIONSHIP-TO-ASSURANCE-018**
Assurance shall evaluate matters requiring semantic judgment.

**DP030-RELATIONSHIP-TO-ASSURANCE-019**
Neither shall independently create persistent normative authority.

**DP030-RELATIONSHIP-TO-ASSURANCE-020**
Persistent semantic change shall return through Governance.
