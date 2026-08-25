---
<!-- DP040-DETAIL-001 -->
doc_id: DP-040
<!-- DP040-DETAIL-002 -->
title: Assurance Architecture Proposal
<!-- DP040-DETAIL-003 -->
status: planning-ready
<!-- DP040-DETAIL-004 -->
depends_on:   - DP-010
<!-- DP040-DETAIL-005 -->
  - DP-020
<!-- DP040-DETAIL-006 -->
  - DP-030
<!-- DP040-DETAIL-007 -->
artifact_type: design-proposal
<!-- DP040-DETAIL-008 -->
canonical_format: markdown
---

# Assurance Architecture Proposal

## Status
<!-- section-id: STATUS -->
<!-- section-id: STATUS -->

<!-- DP040-STATUS-001 -->
Planning-ready Design Proposal.

## Purpose
<!-- section-id: PURPOSE -->
<!-- section-id: PURPOSE -->

<!-- DP040-PURPOSE-001 -->
Define governed semantic review for Design readiness, Plan sufficiency, Build fidelity, and evidence sufficiency.

## Context
<!-- section-id: CONTEXT -->
<!-- section-id: CONTEXT -->

<!-- DP040-CONTEXT-001 -->
Assurance must review semantic properties that cannot be decided mechanically while remaining subordinate to accepted authority.

## Goals
<!-- section-id: GOALS -->
<!-- section-id: GOALS -->

<!-- DP040-GOALS-001 -->
- Preserve the domain architecture and authority boundaries defined by this proposal.
<!-- DP040-GOALS-002 -->
- Make the proposal consumable by incremental functional-set Planning.
<!-- DP040-GOALS-003 -->
- Keep Design statement identity distinct from repository normative identity.

## Non-Goals
<!-- section-id: NON-GOALS -->
<!-- section-id: NON-GOALS -->

<!-- DP040-NON-GOALS-001 -->
- Define one complete implementation plan for the entire proposal.
<!-- DP040-NON-GOALS-002 -->
- Assign repository normative IDs during Design.
<!-- DP040-NON-GOALS-003 -->
- Define file-level pseudo-code in Design unless it is itself a semantic constraint.

## Requirements
<!-- section-id: REQUIREMENTS -->
<!-- section-id: REQUIREMENTS -->

<!-- DP040-REQUIREMENTS-001 -->
The detailed Design below contains addressable Design statements. Statement IDs are non-normative proposal references. `functional-set.json` selects them; `plan.json` owns decomposition and normative distillation.

## Constraints
<!-- section-id: CONSTRAINTS -->
<!-- section-id: CONSTRAINTS -->

<!-- DP040-CONSTRAINTS-001 -->
This proposal remains subordinate to its declared Design dependencies and shall not silently assume authority outside them.

## Architecture
<!-- section-id: ARCHITECTURE -->
<!-- section-id: ARCHITECTURE -->

<!-- DP040-ARCHITECTURE-001 -->
The detailed Design below is semantic input to Planning and may be realized over multiple functional sets.

## Behavior
<!-- section-id: BEHAVIOR -->
<!-- section-id: BEHAVIOR -->

<!-- DP040-BEHAVIOR-001 -->
Planning may consume a bounded subset of this proposal in one functional set; implementation of the entire proposal in one pass is not required.

## Interfaces and Boundaries
<!-- section-id: INTERFACES-AND-BOUNDARIES -->
<!-- section-id: INTERFACES -->

<!-- DP040-INTERFACES-AND-BOUNDARIES-001 -->
Design defines meaning. `functional-set.json` defines selected Design scope. `plan.json` defines normative decomposition and exact implementation intent. Build produces syntactically correct, validated, operational code.

## Invariants
<!-- section-id: INVARIANTS -->
<!-- section-id: INVARIANTS -->

<!-- DP040-INVARIANTS-001 -->
- Design statement IDs remain non-normative.
<!-- DP040-INVARIANTS-002 -->
- Planning owns normative distillation and implementation intent.
<!-- DP040-INVARIANTS-003 -->
- Build shall not invent missing Design semantics or missing Plan intent.

## Alternatives Considered
<!-- section-id: ALTERNATIVES-CONSIDERED -->
<!-- section-id: ALTERNATIVES -->

<!-- DP040-ALTERNATIVES-CONSIDERED-001 -->
Domain-specific alternatives remain in the detailed Design. The revised workflow rejects collapsing Design, Planning, and Build into one artifact or stage.

## Risks and Tradeoffs
<!-- section-id: RISKS-AND-TRADEOFFS -->
<!-- section-id: RISKS -->

<!-- DP040-RISKS-AND-TRADEOFFS-001 -->
Incremental realization may expose missing or ambiguous Design later; those defects must route to Design rather than being silently invented during Planning or Build.

## Open Questions
<!-- section-id: OPEN-QUESTIONS -->
<!-- section-id: OPEN-QUESTIONS -->

<!-- DP040-OPEN-QUESTIONS-001 -->
No blocking workflow-format questions remain. Domain-specific open questions are retained in the detailed Design.

## Acceptance Criteria
<!-- section-id: ACCEPTANCE-CRITERIA -->
<!-- section-id: ACCEPTANCE -->

<!-- DP040-ACCEPTANCE-CRITERIA-001 -->
This proposal is planning-ready when its required sections are complete, its detailed semantics remain coherent with declared dependencies, and its Design statements are addressable.

# Detailed Design

## Framework Contract Basis
<!-- section-id: FRAMEWORK-CONTRACT-BASIS -->

<!-- DP040-FRAMEWORK-CONTRACT-BASIS-001 -->
This proposal assumes the candidate Framework Contract requirements:

<!-- DP040-FRAMEWORK-CONTRACT-BASIS-002 -->
- FC-01 — Framework Authority Location
<!-- DP040-FRAMEWORK-CONTRACT-BASIS-003 -->
- FC-02 — Framework Contract Role
<!-- DP040-FRAMEWORK-CONTRACT-BASIS-004 -->
- FC-03 — Keystone Set
<!-- DP040-FRAMEWORK-CONTRACT-BASIS-005 -->
- FC-04 — Delegated Authority
<!-- DP040-FRAMEWORK-CONTRACT-BASIS-006 -->
- FC-05 — Governance Exclusivity
<!-- DP040-FRAMEWORK-CONTRACT-BASIS-007 -->
- FC-06 — Conformance Exclusivity
<!-- DP040-FRAMEWORK-CONTRACT-BASIS-008 -->
- FC-07 — Assurance Exclusivity
<!-- DP040-FRAMEWORK-CONTRACT-BASIS-009 -->
- FC-08 — Assurance Persistence Boundary
<!-- DP040-FRAMEWORK-CONTRACT-BASIS-010 -->
- FC-09 — Keystone Separation
<!-- DP040-FRAMEWORK-CONTRACT-BASIS-011 -->
- FC-10 — Derived Provenance
<!-- DP040-FRAMEWORK-CONTRACT-BASIS-012 -->
- FC-11 — No Implicit Authority
<!-- DP040-FRAMEWORK-CONTRACT-BASIS-013 -->
- FC-12 — Product Subordination
<!-- DP040-FRAMEWORK-CONTRACT-BASIS-014 -->
- FC-13 — Authority Identity
<!-- DP040-FRAMEWORK-CONTRACT-BASIS-015 -->
- FC-14 — Delegation Resolution

<!-- DP040-FRAMEWORK-CONTRACT-BASIS-016 -->
Assurance shall not assume authority beyond that delegated by the Framework Contract.

## Governance Basis
<!-- section-id: GOVERNANCE-BASIS -->

<!-- DP040-GOVERNANCE-BASIS-001 -->
This proposal assumes the Governance lifecycle:

<!-- DP040-GOVERNANCE-BASIS-002 -->
**Design Proposal**  
<!-- DP040-GOVERNANCE-BASIS-003 -->
→ **Design**  
<!-- DP040-GOVERNANCE-BASIS-004 -->
→ **Plan**  
<!-- DP040-GOVERNANCE-BASIS-005 -->
→ **Build**

<!-- DP040-GOVERNANCE-BASIS-006 -->
Governance owns persistent normative change.

<!-- DP040-GOVERNANCE-BASIS-007 -->
Assurance may provide semantic findings to Governance where accepted Governance authority requires review.

<!-- DP040-GOVERNANCE-BASIS-008 -->
An Assurance finding does not itself create or amend persistent normative authority.

<!-- DP040-GOVERNANCE-BASIS-009 -->
A persistent semantic correction identified through Assurance shall route through Governance Design.

## Conformance Basis
<!-- section-id: CONFORMANCE-BASIS -->

<!-- DP040-CONFORMANCE-BASIS-001 -->
Conformance mechanically evaluates objectively decidable obligations.

<!-- DP040-CONFORMANCE-BASIS-002 -->
Conformance may provide Assurance with:

<!-- DP040-CONFORMANCE-BASIS-003 -->
- mechanical findings;
<!-- DP040-CONFORMANCE-BASIS-004 -->
- correspondence;
<!-- DP040-CONFORMANCE-BASIS-005 -->
- assertion identities;
<!-- DP040-CONFORMANCE-BASIS-006 -->
- evidence;
<!-- DP040-CONFORMANCE-BASIS-007 -->
- closure results; and
<!-- DP040-CONFORMANCE-BASIS-008 -->
- observed state.

<!-- DP040-CONFORMANCE-BASIS-009 -->
Assurance may evaluate the semantic adequacy of those results.

<!-- DP040-CONFORMANCE-BASIS-010 -->
Assurance shall not replace Conformance for mechanically decidable enforcement.

## Objective
<!-- section-id: OBJECTIVE -->

<!-- DP040-OBJECTIVE-001 -->
Assurance shall provide one governed semantic-review architecture in which:

<!-- DP040-OBJECTIVE-002 -->
- every governed semantic review derives from accepted authority;
<!-- DP040-OBJECTIVE-003 -->
- review responsibility is explicit;
<!-- DP040-OBJECTIVE-004 -->
- review scope is explicit;
<!-- DP040-OBJECTIVE-005 -->
- evidence is identifiable;
<!-- DP040-OBJECTIVE-006 -->
- findings are attributable and traceable;
<!-- DP040-OBJECTIVE-007 -->
- interpretation remains within accepted normative semantics;
<!-- DP040-OBJECTIVE-008 -->
- semantic judgment remains bounded to the reviewed case;
<!-- DP040-OBJECTIVE-009 -->
- ambiguity and insufficiency are exposed rather than silently converted into persistent semantics; and
<!-- DP040-OBJECTIVE-010 -->
- persistent semantic change returns through Governance.

<!-- DP040-OBJECTIVE-011 -->
The primary relationship is:

<!-- DP040-OBJECTIVE-012 -->
**accepted normative authority**  
<!-- DP040-OBJECTIVE-013 -->
→ **canonical Assurance correspondence**  
<!-- DP040-OBJECTIVE-014 -->
→ **review obligation**  
<!-- DP040-OBJECTIVE-015 -->
→ **review case**  
<!-- DP040-OBJECTIVE-016 -->
→ **evidence**  
<!-- DP040-OBJECTIVE-017 -->
→ **finding**  
<!-- DP040-OBJECTIVE-018 -->
→ **case disposition or Governance routing**

## Assurance Boundary
<!-- section-id: ASSURANCE-BOUNDARY -->

<!-- DP040-ASSURANCE-BOUNDARY-001 -->
Assurance owns governed semantic review and case-specific semantic judgment.

<!-- DP040-ASSURANCE-BOUNDARY-002 -->
Assurance may:

<!-- DP040-ASSURANCE-BOUNDARY-003 -->
- evaluate semantic clarity;
<!-- DP040-ASSURANCE-BOUNDARY-004 -->
- evaluate normative requirement quality;
<!-- DP040-ASSURANCE-BOUNDARY-005 -->
- identify ambiguity;
<!-- DP040-ASSURANCE-BOUNDARY-006 -->
- identify contradiction;
<!-- DP040-ASSURANCE-BOUNDARY-007 -->
- identify omission;
<!-- DP040-ASSURANCE-BOUNDARY-008 -->
- identify overlap;
<!-- DP040-ASSURANCE-BOUNDARY-009 -->
- identify inappropriate implementation leakage;
<!-- DP040-ASSURANCE-BOUNDARY-010 -->
- evaluate evidence sufficiency;
<!-- DP040-ASSURANCE-BOUNDARY-011 -->
- evaluate Conformance interpretation;
<!-- DP040-ASSURANCE-BOUNDARY-012 -->
- evaluate realization fidelity;
<!-- DP040-ASSURANCE-BOUNDARY-013 -->
- issue case-specific findings; and
<!-- DP040-ASSURANCE-BOUNDARY-014 -->
- identify defects requiring Governance action.

<!-- DP040-ASSURANCE-BOUNDARY-015 -->
Assurance shall not:

<!-- DP040-ASSURANCE-BOUNDARY-016 -->
- create persistent normative authority;
<!-- DP040-ASSURANCE-BOUNDARY-017 -->
- amend accepted normative authority;
<!-- DP040-ASSURANCE-BOUNDARY-018 -->
- extend or narrow accepted normative semantics;
<!-- DP040-ASSURANCE-BOUNDARY-019 -->
- convert reviewer preference into authority;
<!-- DP040-ASSURANCE-BOUNDARY-020 -->
- mechanically enforce obligations reserved to Conformance;
<!-- DP040-ASSURANCE-BOUNDARY-021 -->
- redefine Conformance predicates directly;
<!-- DP040-ASSURANCE-BOUNDARY-022 -->
- redefine Governance authority; or
<!-- DP040-ASSURANCE-BOUNDARY-023 -->
- convert prior findings into persistent precedent without accepted authority.

## Assurance Terminology
<!-- section-id: ASSURANCE-TERMINOLOGY -->

### Assurance Primitive
<!-- section-id: ASSURANCE-PRIMITIVE -->

<!-- DP040-ASSURANCE-PRIMITIVE-001 -->
A maintained artifact whose purpose participates in governed semantic review.

<!-- DP040-ASSURANCE-PRIMITIVE-002 -->
Assurance primitives may include:

<!-- DP040-ASSURANCE-PRIMITIVE-003 -->
- Assurance correspondence;
<!-- DP040-ASSURANCE-PRIMITIVE-004 -->
- review obligations;
<!-- DP040-ASSURANCE-PRIMITIVE-005 -->
- review cases;
<!-- DP040-ASSURANCE-PRIMITIVE-006 -->
- evidence manifests;
<!-- DP040-ASSURANCE-PRIMITIVE-007 -->
- reviewer instructions;
<!-- DP040-ASSURANCE-PRIMITIVE-008 -->
- rubrics;
<!-- DP040-ASSURANCE-PRIMITIVE-009 -->
- findings;
<!-- DP040-ASSURANCE-PRIMITIVE-010 -->
- dispositions;
<!-- DP040-ASSURANCE-PRIMITIVE-011 -->
- semantic checklists;
<!-- DP040-ASSURANCE-PRIMITIVE-012 -->
- Assurance schemas; and
<!-- DP040-ASSURANCE-PRIMITIVE-013 -->
- generated Assurance views.

### Assurance Correspondence
<!-- section-id: ASSURANCE-CORRESPONDENCE -->

<!-- DP040-ASSURANCE-CORRESPONDENCE-001 -->
The governed relationship between accepted authority and Assurance responsibility.

<!-- DP040-ASSURANCE-CORRESPONDENCE-002 -->
Assurance correspondence identifies whether semantic-review responsibility exists and, where applicable, the review obligations derived from that authority.

<!-- DP040-ASSURANCE-CORRESPONDENCE-003 -->
Correspondence does not independently own normative semantics.

### Review Obligation
<!-- section-id: REVIEW-OBLIGATION -->

<!-- DP040-REVIEW-OBLIGATION-001 -->
An independently identifiable semantic-review responsibility derived from accepted authority.

<!-- DP040-REVIEW-OBLIGATION-002 -->
A review obligation defines why governed semantic review is required.

### Review Case
<!-- section-id: REVIEW-CASE -->

<!-- DP040-REVIEW-CASE-001 -->
A bounded invocation of one or more review obligations against identified subject matter and evidence.

<!-- DP040-REVIEW-CASE-002 -->
A review case provides the context within which Assurance judgment is valid.

### Evidence
<!-- section-id: EVIDENCE -->

<!-- DP040-EVIDENCE-001 -->
Information considered by Assurance in a review case.

<!-- DP040-EVIDENCE-002 -->
Evidence may include:

<!-- DP040-EVIDENCE-003 -->
- accepted normative authority;
<!-- DP040-EVIDENCE-004 -->
- Governance artifacts;
<!-- DP040-EVIDENCE-005 -->
- Conformance findings;
<!-- DP040-EVIDENCE-006 -->
- Conformance correspondence;
<!-- DP040-EVIDENCE-007 -->
- implementation;
<!-- DP040-EVIDENCE-008 -->
- repository state;
<!-- DP040-EVIDENCE-009 -->
- generated artifacts;
<!-- DP040-EVIDENCE-010 -->
- historical provenance; and
<!-- DP040-EVIDENCE-011 -->
- prior Assurance findings.

<!-- DP040-EVIDENCE-012 -->
Evidence does not acquire normative authority merely because it is considered during review.

### Finding
<!-- section-id: FINDING -->

<!-- DP040-FINDING-001 -->
A governed semantic conclusion produced for a review case.

<!-- DP040-FINDING-002 -->
A finding remains bounded to that case unless persistent semantics are subsequently established through Governance.

## Closed Assurance Hierarchy
<!-- section-id: CLOSED-ASSURANCE-HIERARCHY -->

<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-001 -->
Governed semantic review shall occur only through the authorized Assurance hierarchy.

<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-002 -->
A maintained artifact whose purpose participates in governed semantic review shall participate in that hierarchy.

<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-003 -->
Applicable artifacts may include:

<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-004 -->
- Assurance correspondence;
<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-005 -->
- review obligations;
<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-006 -->
- review cases;
<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-007 -->
- evidence manifests;
<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-008 -->
- reviewer instructions;
<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-009 -->
- rubrics;
<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-010 -->
- findings;
<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-011 -->
- dispositions;
<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-012 -->
- semantic checklists;
<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-013 -->
- Assurance schemas; and
<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-014 -->
- generated Assurance views.

<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-015 -->
Artifacts outside the governed Assurance hierarchy shall not independently produce governed Assurance findings.

<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-016 -->
General analysis may inform Assurance.

<!-- DP040-CLOSED-ASSURANCE-HIERARCHY-017 -->
It does not acquire Assurance authority merely because it exists.

## Purpose of the Closed Hierarchy
<!-- section-id: PURPOSE-OF-THE-CLOSED-HIERARCHY -->

<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-001 -->
The closed Assurance hierarchy is an authority-control mechanism.

<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-002 -->
It prevents:

<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-003 -->
- reviewer preference becoming policy;
<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-004 -->
- AI interpretation becoming implicit authority;
<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-005 -->
- findings with no normative basis;
<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-006 -->
- reviews with undefined scope;
<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-007 -->
- findings disconnected from evidence;
<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-008 -->
- findings disconnected from authority;
<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-009 -->
- repeated conclusions becoming undeclared precedent;
<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-010 -->
- ad hoc semantic gates; and
<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-011 -->
- semantic obligations hidden outside governed review structure.

<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-012 -->
The expected relationship is:

<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-013 -->
**accepted authority**  
<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-014 -->
→ **canonical Assurance correspondence**  
<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-015 -->
→ **review obligation**  
<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-016 -->
→ **review case**  
<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-017 -->
→ **evidence**  
<!-- DP040-PURPOSE-OF-THE-CLOSED-HIERARCHY-018 -->
→ **finding**

## Canonical Assurance Correspondence
<!-- section-id: CANONICAL-ASSURANCE-CORRESPONDENCE -->

<!-- DP040-CANONICAL-ASSURANCE-CORRESPONDENCE-001 -->
Each active normative requirement shall have exactly one canonical Assurance correspondence record.

<!-- DP040-CANONICAL-ASSURANCE-CORRESPONDENCE-002 -->
The correspondence shall identify:

<!-- DP040-CANONICAL-ASSURANCE-CORRESPONDENCE-003 -->
- normative requirement identity;
<!-- DP040-CANONICAL-ASSURANCE-CORRESPONDENCE-004 -->
- Assurance applicability; and
<!-- DP040-CANONICAL-ASSURANCE-CORRESPONDENCE-005 -->
- applicable review obligations where Assurance is required.

<!-- DP040-CANONICAL-ASSURANCE-CORRESPONDENCE-006 -->
The correspondence record shall not restate normative requirement semantics as independent authority.

## Assurance Applicability
<!-- section-id: ASSURANCE-APPLICABILITY -->

<!-- DP040-ASSURANCE-APPLICABILITY-001 -->
Each active normative requirement shall have exactly one canonical Assurance applicability determination.

<!-- DP040-ASSURANCE-APPLICABILITY-002 -->
The candidate vocabulary is:

### `required`
<!-- section-id: REQUIRED -->

<!-- DP040-REQUIRED-001 -->
The normative requirement has governed semantic-review responsibility.

<!-- DP040-REQUIRED-002 -->
At least one review obligation shall exist.

### `none`
<!-- section-id: NONE -->

<!-- DP040-NONE-001 -->
No Assurance responsibility exists for the normative requirement under accepted authority.

<!-- DP040-NONE-002 -->
A rationale may be required where absence of Assurance responsibility is not self-evident.

<!-- DP040-NONE-003 -->
Assurance applicability describes only Assurance responsibility.

<!-- DP040-NONE-004 -->
It does not encode Conformance responsibility.

## Cross-Keystone Applicability
<!-- section-id: CROSS-KEYSTONE-APPLICABILITY -->

<!-- DP040-CROSS-KEYSTONE-APPLICABILITY-001 -->
Conformance and Assurance applicability are independent dimensions.

<!-- DP040-CROSS-KEYSTONE-APPLICABILITY-002 -->
A requirement may therefore be:

| Conformance | Assurance | Meaning |
| --- | --- | --- |
| mechanical | none | mechanical enforcement only |
| none | required | semantic review only |
| mechanical | required | both mechanical and semantic responsibility |
| none | none | neither keystone directly evaluates the requirement |

<!-- DP040-CROSS-KEYSTONE-APPLICABILITY-003 -->
The final combination should be explicitly justified where meaningful enforcement or review might otherwise be expected.

<!-- DP040-CROSS-KEYSTONE-APPLICABILITY-004 -->
This model replaces overloaded concepts such as `partial` or `semantic-review` dispositions spanning multiple keystones.

## Review Obligation Model
<!-- section-id: REVIEW-OBLIGATION-MODEL -->

<!-- DP040-REVIEW-OBLIGATION-MODEL-001 -->
A review obligation represents one independently identifiable semantic-review responsibility.

<!-- DP040-REVIEW-OBLIGATION-MODEL-002 -->
Examples may include:

<!-- DP040-REVIEW-OBLIGATION-MODEL-003 -->
- ambiguity review;
<!-- DP040-REVIEW-OBLIGATION-MODEL-004 -->
- requirement-quality review;
<!-- DP040-REVIEW-OBLIGATION-MODEL-005 -->
- Conformance-applicability review;
<!-- DP040-REVIEW-OBLIGATION-MODEL-006 -->
- assertion-interpretation review;
<!-- DP040-REVIEW-OBLIGATION-MODEL-007 -->
- evidence-sufficiency review;
<!-- DP040-REVIEW-OBLIGATION-MODEL-008 -->
- realization-fidelity review;
<!-- DP040-REVIEW-OBLIGATION-MODEL-009 -->
- conflict review; and
<!-- DP040-REVIEW-OBLIGATION-MODEL-010 -->
- Governance-stage review.

<!-- DP040-REVIEW-OBLIGATION-MODEL-011 -->
A normative requirement or other accepted framework authority may derive multiple review obligations.

<!-- DP040-REVIEW-OBLIGATION-MODEL-012 -->
Review-obligation identity is distinct from:

<!-- DP040-REVIEW-OBLIGATION-MODEL-013 -->
- normative requirement identity;
<!-- DP040-REVIEW-OBLIGATION-MODEL-014 -->
- review-case identity;
<!-- DP040-REVIEW-OBLIGATION-MODEL-015 -->
- reviewer identity; and
<!-- DP040-REVIEW-OBLIGATION-MODEL-016 -->
- finding identity.

## Review Obligation Authority
<!-- section-id: REVIEW-OBLIGATION-AUTHORITY -->

<!-- DP040-REVIEW-OBLIGATION-AUTHORITY-001 -->
Every maintained review obligation shall resolve to accepted authority requiring or authorizing the review.

<!-- DP040-REVIEW-OBLIGATION-AUTHORITY-002 -->
Assurance shall not create mandatory semantic-review obligations merely because additional review appears useful.

<!-- DP040-REVIEW-OBLIGATION-AUTHORITY-003 -->
Exploratory analysis may occur without becoming governed Assurance responsibility.

## Assurance Provenance
<!-- section-id: ASSURANCE-PROVENANCE -->

<!-- DP040-ASSURANCE-PROVENANCE-001 -->
Every maintained Assurance primitive shall resolve through governed provenance to accepted authority.

<!-- DP040-ASSURANCE-PROVENANCE-002 -->
The provenance chain shall permit resolution of:

<!-- DP040-ASSURANCE-PROVENANCE-003 -->
**accepted authority**  
<!-- DP040-ASSURANCE-PROVENANCE-004 -->
→ **review obligation**  
<!-- DP040-ASSURANCE-PROVENANCE-005 -->
→ **review case**  
<!-- DP040-ASSURANCE-PROVENANCE-006 -->
→ **finding**

<!-- DP040-ASSURANCE-PROVENANCE-007 -->
Evidence used by a finding shall also be identifiable.

<!-- DP040-ASSURANCE-PROVENANCE-008 -->
No orphan Assurance finding is permitted.

## Review Case Identity
<!-- section-id: REVIEW-CASE-IDENTITY -->

<!-- DP040-REVIEW-CASE-IDENTITY-001 -->
Each governed Assurance review case shall have a stable unique identity.

<!-- DP040-REVIEW-CASE-IDENTITY-002 -->
Case identity shall be distinct from:

<!-- DP040-REVIEW-CASE-IDENTITY-003 -->
- normative requirement identity;
<!-- DP040-REVIEW-CASE-IDENTITY-004 -->
- review-obligation identity;
<!-- DP040-REVIEW-CASE-IDENTITY-005 -->
- reviewer identity; and
<!-- DP040-REVIEW-CASE-IDENTITY-006 -->
- finding identity.

<!-- DP040-REVIEW-CASE-IDENTITY-007 -->
This permits repeated reviews against the same authority without conflating their conclusions.

## Review Scope
<!-- section-id: REVIEW-SCOPE -->

<!-- DP040-REVIEW-SCOPE-001 -->
Every review case shall explicitly define its scope.

<!-- DP040-REVIEW-SCOPE-002 -->
A review case shall distinguish:

<!-- DP040-REVIEW-SCOPE-003 -->
- **authorizing authority** — accepted authority that requires or permits Assurance to perform the review; and
<!-- DP040-REVIEW-SCOPE-004 -->
- **review subject** — the candidate authority, accepted authority, Governance artifact, Conformance artifact, implementation, repository state, or other material being evaluated.

<!-- DP040-REVIEW-SCOPE-005 -->
This distinction permits Assurance to review non-authoritative candidates without allowing the candidate to authorize its own review.

<!-- DP040-REVIEW-SCOPE-006 -->
Scope shall identify, as applicable:

<!-- DP040-REVIEW-SCOPE-007 -->
- authorizing authority;
<!-- DP040-REVIEW-SCOPE-008 -->
- reviewed subject matter;
<!-- DP040-REVIEW-SCOPE-009 -->
- review obligations being exercised;
<!-- DP040-REVIEW-SCOPE-010 -->
- Governance artifact or stage under review;
<!-- DP040-REVIEW-SCOPE-011 -->
- Conformance correspondence or assertions under review;
<!-- DP040-REVIEW-SCOPE-012 -->
- implementation or repository state under review;
<!-- DP040-REVIEW-SCOPE-013 -->
- relevant evidence; and
<!-- DP040-REVIEW-SCOPE-014 -->
- relevant exclusions.

<!-- DP040-REVIEW-SCOPE-015 -->
A finding shall not silently claim semantic effect outside the defined review scope.

## Finding Identity
<!-- section-id: FINDING-IDENTITY -->

<!-- DP040-FINDING-IDENTITY-001 -->
Each maintained Assurance finding shall have a stable identity within its review case.

<!-- DP040-FINDING-IDENTITY-002 -->
A finding identity shall not be reused for an unrelated conclusion.

<!-- DP040-FINDING-IDENTITY-003 -->
Findings participating in Governance lineage or later evidence shall remain historically resolvable.

## Finding Traceability
<!-- section-id: FINDING-TRACEABILITY -->

<!-- DP040-FINDING-TRACEABILITY-001 -->
Each Assurance finding shall resolve to:

<!-- DP040-FINDING-TRACEABILITY-002 -->
- its review case;
<!-- DP040-FINDING-TRACEABILITY-003 -->
- applicable review obligation;
<!-- DP040-FINDING-TRACEABILITY-004 -->
- authorizing authority;
<!-- DP040-FINDING-TRACEABILITY-005 -->
- reviewed subject matter; and
<!-- DP040-FINDING-TRACEABILITY-006 -->
- evidence basis.

<!-- DP040-FINDING-TRACEABILITY-007 -->
A finding should distinguish:

<!-- DP040-FINDING-TRACEABILITY-008 -->
- observation;
<!-- DP040-FINDING-TRACEABILITY-009 -->
- semantic analysis;
<!-- DP040-FINDING-TRACEABILITY-010 -->
- conclusion; and
<!-- DP040-FINDING-TRACEABILITY-011 -->
- recommended action.

<!-- DP040-FINDING-TRACEABILITY-012 -->
The exact representation belongs in subordinate Assurance authority.

## Review Execution Closure
<!-- section-id: REVIEW-EXECUTION-CLOSURE -->

<!-- DP040-REVIEW-EXECUTION-CLOSURE-001 -->
A review obligation may exist without being continuously active.

<!-- DP040-REVIEW-EXECUTION-CLOSURE-002 -->
When accepted authority triggers a review obligation for a governed decision, that obligation shall be realized by a governed review case before the decision may be accepted.

<!-- DP040-REVIEW-EXECUTION-CLOSURE-003 -->
A declared review obligation that is triggered but never instantiated does not satisfy Assurance responsibility.

## Assurance Semantic Boundary
<!-- section-id: ASSURANCE-SEMANTIC-BOUNDARY -->

<!-- DP040-ASSURANCE-SEMANTIC-BOUNDARY-001 -->
Assurance judgment is bounded to the authorized review case in which it is issued.

<!-- DP040-ASSURANCE-SEMANTIC-BOUNDARY-002 -->
An Assurance finding shall not independently:

<!-- DP040-ASSURANCE-SEMANTIC-BOUNDARY-003 -->
- create normative authority;
<!-- DP040-ASSURANCE-SEMANTIC-BOUNDARY-004 -->
- amend normative authority;
<!-- DP040-ASSURANCE-SEMANTIC-BOUNDARY-005 -->
- supersede normative authority;
<!-- DP040-ASSURANCE-SEMANTIC-BOUNDARY-006 -->
- withdraw normative authority;
<!-- DP040-ASSURANCE-SEMANTIC-BOUNDARY-007 -->
- establish persistent normative semantics beyond the reviewed case; or
<!-- DP040-ASSURANCE-SEMANTIC-BOUNDARY-008 -->
- establish persistent precedent.

<!-- DP040-ASSURANCE-SEMANTIC-BOUNDARY-009 -->
A case-specific finding may affect disposition of the reviewed case where accepted authority grants that effect.

<!-- DP040-ASSURANCE-SEMANTIC-BOUNDARY-010 -->
Persistent semantic effect requires Governance.

## Interpretation Boundary
<!-- section-id: INTERPRETATION-BOUNDARY -->

<!-- DP040-INTERPRETATION-BOUNDARY-001 -->
Assurance may interpret accepted authority when necessary to decide a bounded review case.

<!-- DP040-INTERPRETATION-BOUNDARY-002 -->
Interpretation shall remain anchored to accepted normative semantics.

<!-- DP040-INTERPRETATION-BOUNDARY-003 -->
Assurance shall not independently:

<!-- DP040-INTERPRETATION-BOUNDARY-004 -->
- manufacture missing obligations;
<!-- DP040-INTERPRETATION-BOUNDARY-005 -->
- broaden accepted obligations;
<!-- DP040-INTERPRETATION-BOUNDARY-006 -->
- narrow accepted obligations;
<!-- DP040-INTERPRETATION-BOUNDARY-007 -->
- convert implementation preference into semantics; or
<!-- DP040-INTERPRETATION-BOUNDARY-008 -->
- permanently settle unresolved ambiguity.

<!-- DP040-INTERPRETATION-BOUNDARY-009 -->
Where materially different interpretations remain reasonable, Assurance should identify ambiguity rather than create persistent resolution.

## Governance Routing
<!-- section-id: GOVERNANCE-ROUTING -->

<!-- DP040-GOVERNANCE-ROUTING-001 -->
A finding requiring persistent normative semantic change shall route through Governance Design.

<!-- DP040-GOVERNANCE-ROUTING-002 -->
Examples include:

<!-- DP040-GOVERNANCE-ROUTING-003 -->
- ambiguous accepted authority;
<!-- DP040-GOVERNANCE-ROUTING-004 -->
- contradictory authority;
<!-- DP040-GOVERNANCE-ROUTING-005 -->
- missing normative semantics;
<!-- DP040-GOVERNANCE-ROUTING-006 -->
- requirement-quality defects requiring rewritten authority;
<!-- DP040-GOVERNANCE-ROUTING-007 -->
- persistent interpretation disputes; and
<!-- DP040-GOVERNANCE-ROUTING-008 -->
- desired precedent not already established by accepted authority.

<!-- DP040-GOVERNANCE-ROUTING-009 -->
Assurance identifies the semantic defect.

<!-- DP040-GOVERNANCE-ROUTING-010 -->
Governance owns its persistent resolution.

## Finding Classes
<!-- section-id: FINDING-CLASSES -->

<!-- DP040-FINDING-CLASSES-001 -->
Assurance may distinguish finding classes such as:

### `satisfied`
<!-- section-id: SATISFIED -->

<!-- DP040-SATISFIED-001 -->
The reviewed semantic responsibility is adequately satisfied for the bounded case.

### `concern`
<!-- section-id: CONCERN -->

<!-- DP040-CONCERN-001 -->
A semantic issue exists but does not necessarily prevent disposition.

### `insufficient`
<!-- section-id: INSUFFICIENT -->

<!-- DP040-INSUFFICIENT-001 -->
Available evidence or reasoning is insufficient to establish the required conclusion.

### `ambiguous`
<!-- section-id: AMBIGUOUS -->

<!-- DP040-AMBIGUOUS-001 -->
Accepted authority supports materially different relevant interpretations.

### `contradictory`
<!-- section-id: CONTRADICTORY -->

<!-- DP040-CONTRADICTORY-001 -->
Applicable accepted authority contains incompatible semantics.

### `defect`
<!-- section-id: DEFECT -->

<!-- DP040-DEFECT-001 -->
The reviewed realization, correspondence, or interpretation conflicts with accepted authority.

### `governance-required`
<!-- section-id: GOVERNANCE-REQUIRED -->

<!-- DP040-GOVERNANCE-REQUIRED-001 -->
Persistent normative action is required before the semantic issue can be properly resolved.

<!-- DP040-GOVERNANCE-REQUIRED-002 -->
The exact vocabulary belongs in subordinate Assurance design.

## Evidence Sufficiency
<!-- section-id: EVIDENCE-SUFFICIENCY -->

<!-- DP040-EVIDENCE-SUFFICIENCY-001 -->
Assurance may evaluate whether evidence is semantically sufficient for a governed claim.

<!-- DP040-EVIDENCE-SUFFICIENCY-002 -->
Evidence sufficiency is distinct from evidence existence.

<!-- DP040-EVIDENCE-SUFFICIENCY-003 -->
Conformance may mechanically determine:

<!-- DP040-EVIDENCE-SUFFICIENCY-004 -->
- whether evidence exists;
<!-- DP040-EVIDENCE-SUFFICIENCY-005 -->
- whether required evidence categories are present; and
<!-- DP040-EVIDENCE-SUFFICIENCY-006 -->
- whether evidence conforms structurally.

<!-- DP040-EVIDENCE-SUFFICIENCY-007 -->
Assurance may determine:

<!-- DP040-EVIDENCE-SUFFICIENCY-008 -->
- whether evidence meaningfully supports the claimed conclusion;
<!-- DP040-EVIDENCE-SUFFICIENCY-009 -->
- whether evidence scope matches the claim;
<!-- DP040-EVIDENCE-SUFFICIENCY-010 -->
- whether relevant cases are omitted;
<!-- DP040-EVIDENCE-SUFFICIENCY-011 -->
- whether evidence relies on incorrect semantic interpretation; and
<!-- DP040-EVIDENCE-SUFFICIENCY-012 -->
- whether the evidence is sufficient for the governed review purpose.

<!-- DP040-EVIDENCE-SUFFICIENCY-013 -->
Detailed evidence-sufficiency policies belong in subordinate Assurance authority.

## Normative Requirement Quality
<!-- section-id: NORMATIVE-REQUIREMENT-QUALITY -->

<!-- DP040-NORMATIVE-REQUIREMENT-QUALITY-001 -->
Assurance may evaluate semantic properties of normative requirements that cannot be reliably decided mechanically.

<!-- DP040-NORMATIVE-REQUIREMENT-QUALITY-002 -->
Examples include:

<!-- DP040-NORMATIVE-REQUIREMENT-QUALITY-003 -->
- atomicity;
<!-- DP040-NORMATIVE-REQUIREMENT-QUALITY-004 -->
- clarity;
<!-- DP040-NORMATIVE-REQUIREMENT-QUALITY-005 -->
- ambiguity;
<!-- DP040-NORMATIVE-REQUIREMENT-QUALITY-006 -->
- contradiction;
<!-- DP040-NORMATIVE-REQUIREMENT-QUALITY-007 -->
- overlap;
<!-- DP040-NORMATIVE-REQUIREMENT-QUALITY-008 -->
- duplication;
<!-- DP040-NORMATIVE-REQUIREMENT-QUALITY-009 -->
- inappropriate implementation leakage;
<!-- DP040-NORMATIVE-REQUIREMENT-QUALITY-010 -->
- undefined subjective qualifiers;
<!-- DP040-NORMATIVE-REQUIREMENT-QUALITY-011 -->
- hidden obligations inside rationale; and
<!-- DP040-NORMATIVE-REQUIREMENT-QUALITY-012 -->
- inappropriate coupling of independent obligations.

<!-- DP040-NORMATIVE-REQUIREMENT-QUALITY-013 -->
Assurance findings about requirement quality do not themselves amend the requirement.

<!-- DP040-NORMATIVE-REQUIREMENT-QUALITY-014 -->
Persistent correction occurs through Governance.

## Mechanical Quality and Semantic Quality
<!-- section-id: MECHANICAL-QUALITY-AND-SEMANTIC-QUALITY -->

<!-- DP040-MECHANICAL-QUALITY-AND-SEMANTIC-QUALITY-001 -->
Requirement quality spans multiple keystones.

<!-- DP040-MECHANICAL-QUALITY-AND-SEMANTIC-QUALITY-002 -->
**Governance** owns creation and acceptance of normative authority.

<!-- DP040-MECHANICAL-QUALITY-AND-SEMANTIC-QUALITY-003 -->
**Conformance** may mechanically enforce objectively decidable structural quality rules.

<!-- DP040-MECHANICAL-QUALITY-AND-SEMANTIC-QUALITY-004 -->
**Assurance** may evaluate semantic quality requiring judgment.

<!-- DP040-MECHANICAL-QUALITY-AND-SEMANTIC-QUALITY-005 -->
No keystone gains the authority of another merely because all three participate in requirement quality.

## Conformance Review
<!-- section-id: CONFORMANCE-REVIEW -->

<!-- DP040-CONFORMANCE-REVIEW-001 -->
Where authorized, Assurance may evaluate whether Conformance faithfully represents accepted normative authority.

<!-- DP040-CONFORMANCE-REVIEW-002 -->
Assurance may review:

<!-- DP040-CONFORMANCE-REVIEW-003 -->
- Conformance applicability;
<!-- DP040-CONFORMANCE-REVIEW-004 -->
- assertion decomposition;
<!-- DP040-CONFORMANCE-REVIEW-005 -->
- assertion interpretation;
<!-- DP040-CONFORMANCE-REVIEW-006 -->
- evidence sufficiency;
<!-- DP040-CONFORMANCE-REVIEW-007 -->
- over-enforcement;
<!-- DP040-CONFORMANCE-REVIEW-008 -->
- under-enforcement; and
<!-- DP040-CONFORMANCE-REVIEW-009 -->
- claims of mechanical decidability.

<!-- DP040-CONFORMANCE-REVIEW-010 -->
Assurance may issue findings about Conformance.

<!-- DP040-CONFORMANCE-REVIEW-011 -->
It shall not directly create persistent Conformance semantics.

<!-- DP040-CONFORMANCE-REVIEW-012 -->
Persistent correction routes through Governance.

## Realization Fidelity
<!-- section-id: REALIZATION-FIDELITY -->

<!-- DP040-REALIZATION-FIDELITY-001 -->
Where authorized, Assurance may review whether realization faithfully reflects accepted normative intent.

<!-- DP040-REALIZATION-FIDELITY-002 -->
This review may identify semantic defects not completely captured by mechanical assertions.

<!-- DP040-REALIZATION-FIDELITY-003 -->
Examples include:

<!-- DP040-REALIZATION-FIDELITY-004 -->
- semantic omission;
<!-- DP040-REALIZATION-FIDELITY-005 -->
- inappropriate abstraction;
<!-- DP040-REALIZATION-FIDELITY-006 -->
- unintended interpretation;
<!-- DP040-REALIZATION-FIDELITY-007 -->
- misleading derived documentation; and
<!-- DP040-REALIZATION-FIDELITY-008 -->
- mechanically valid but semantically inadequate realization.

<!-- DP040-REALIZATION-FIDELITY-009 -->
Assurance shall not rewrite authority to conform to existing implementation.

## Governance Stage Review
<!-- section-id: GOVERNANCE-STAGE-REVIEW -->

<!-- DP040-GOVERNANCE-STAGE-REVIEW-001 -->
Governance may require Assurance at defined stage gates.

### Design Assurance
<!-- section-id: DESIGN-ASSURANCE -->

<!-- DP040-DESIGN-ASSURANCE-001 -->
May evaluate:

<!-- DP040-DESIGN-ASSURANCE-002 -->
- requirement quality;
<!-- DP040-DESIGN-ASSURANCE-003 -->
- semantic clarity;
<!-- DP040-DESIGN-ASSURANCE-004 -->
- atomicity;
<!-- DP040-DESIGN-ASSURANCE-005 -->
- internal consistency;
<!-- DP040-DESIGN-ASSURANCE-006 -->
- authority boundaries; and
<!-- DP040-DESIGN-ASSURANCE-007 -->
- unresolved ambiguity.

### Plan Assurance
<!-- section-id: PLAN-ASSURANCE -->

<!-- DP040-PLAN-ASSURANCE-001 -->
May evaluate:

<!-- DP040-PLAN-ASSURANCE-002 -->
- fidelity to accepted Design;
<!-- DP040-PLAN-ASSURANCE-003 -->
- semantic completeness of realization intent;
<!-- DP040-PLAN-ASSURANCE-004 -->
- inappropriate reinterpretation; and
<!-- DP040-PLAN-ASSURANCE-005 -->
- adequacy of planned semantic evidence.

### Build Assurance
<!-- section-id: BUILD-ASSURANCE -->

<!-- DP040-BUILD-ASSURANCE-001 -->
May evaluate:

<!-- DP040-BUILD-ASSURANCE-002 -->
- realization fidelity;
<!-- DP040-BUILD-ASSURANCE-003 -->
- evidence sufficiency;
<!-- DP040-BUILD-ASSURANCE-004 -->
- semantic fidelity of Conformance; and
<!-- DP040-BUILD-ASSURANCE-005 -->
- unresolved semantic defects.

<!-- DP040-BUILD-ASSURANCE-006 -->
Governance decides whether review is required.

<!-- DP040-BUILD-ASSURANCE-007 -->
Assurance produces the finding.

<!-- DP040-BUILD-ASSURANCE-008 -->
Governance performs acceptance.

## Reviewer Attribution
<!-- section-id: REVIEWER-ATTRIBUTION -->

<!-- DP040-REVIEWER-ATTRIBUTION-001 -->
Assurance findings shall be attributable to the actor or governed actor class responsible for review.

<!-- DP040-REVIEWER-ATTRIBUTION-002 -->
Reviewers may include:

<!-- DP040-REVIEWER-ATTRIBUTION-003 -->
- humans;
<!-- DP040-REVIEWER-ATTRIBUTION-004 -->
- AI agents;
<!-- DP040-REVIEWER-ATTRIBUTION-005 -->
- automated semantic systems; or
<!-- DP040-REVIEWER-ATTRIBUTION-006 -->
- governed combinations of actors.

<!-- DP040-REVIEWER-ATTRIBUTION-007 -->
Reviewer identity does not create authority.

<!-- DP040-REVIEWER-ATTRIBUTION-008 -->
The reviewer's ability, expertise, confidence, or implementation access does not independently enlarge Assurance authority.

## Human and AI Review
<!-- section-id: HUMAN-AND-AI-REVIEW -->

<!-- DP040-HUMAN-AND-AI-REVIEW-001 -->
Human and AI reviewers are subject to the same accepted Assurance boundaries.

<!-- DP040-HUMAN-AND-AI-REVIEW-002 -->
AI-assisted review may be useful for:

<!-- DP040-HUMAN-AND-AI-REVIEW-003 -->
- ambiguity detection;
<!-- DP040-HUMAN-AND-AI-REVIEW-004 -->
- requirement-decomposition analysis;
<!-- DP040-HUMAN-AND-AI-REVIEW-005 -->
- cross-specification consistency review;
<!-- DP040-HUMAN-AND-AI-REVIEW-006 -->
- provenance review;
<!-- DP040-HUMAN-AND-AI-REVIEW-007 -->
- evidence analysis; and
<!-- DP040-HUMAN-AND-AI-REVIEW-008 -->
- implementation-to-authority comparison.

<!-- DP040-HUMAN-AND-AI-REVIEW-009 -->
An AI reviewer shall not:

<!-- DP040-HUMAN-AND-AI-REVIEW-010 -->
- treat confidence as authority;
<!-- DP040-HUMAN-AND-AI-REVIEW-011 -->
- invent persistent semantics;
<!-- DP040-HUMAN-AND-AI-REVIEW-012 -->
- create undeclared precedent;
<!-- DP040-HUMAN-AND-AI-REVIEW-013 -->
- infer authority from implementation;
<!-- DP040-HUMAN-AND-AI-REVIEW-014 -->
- waive Governance obligations; or
<!-- DP040-HUMAN-AND-AI-REVIEW-015 -->
- waive Conformance obligations.

<!-- DP040-HUMAN-AND-AI-REVIEW-016 -->
Human reviewers shall not acquire those powers merely through judgment or expertise either.

## Prior Findings
<!-- section-id: PRIOR-FINDINGS -->

<!-- DP040-PRIOR-FINDINGS-001 -->
Prior Assurance findings may be evidence in later review cases.

<!-- DP040-PRIOR-FINDINGS-002 -->
Prior findings are not automatically binding precedent.

<!-- DP040-PRIOR-FINDINGS-003 -->
Absent accepted authority establishing a precedent model, a prior finding remains a case-specific conclusion.

<!-- DP040-PRIOR-FINDINGS-004 -->
Repeated identical findings do not independently transform the conclusion into persistent normative authority.

## Conflicting Findings
<!-- section-id: CONFLICTING-FINDINGS -->

<!-- DP040-CONFLICTING-FINDINGS-001 -->
Multiple Assurance cases may produce materially conflicting findings.

<!-- DP040-CONFLICTING-FINDINGS-002 -->
Conflict shall remain explicit until resolved through an authorized governed mechanism.

<!-- DP040-CONFLICTING-FINDINGS-003 -->
Assurance shall not hide the conflict by selecting one preferred interpretation as persistent semantics.

<!-- DP040-CONFLICTING-FINDINGS-004 -->
If persistent semantic resolution is required, the conflict shall route through Governance.

## Single Assurance Correspondence Authority
<!-- section-id: SINGLE-ASSURANCE-CORRESPONDENCE-AUTHORIT -->

<!-- DP040-SINGLE-ASSURANCE-CORRESPONDENCE-AUTHORIT-001 -->
Assurance shall define one canonical authority for requirement-to-Assurance correspondence.

<!-- DP040-SINGLE-ASSURANCE-CORRESPONDENCE-AUTHORIT-002 -->
Independently maintained mappings shall not be allowed to silently diverge.

<!-- DP040-SINGLE-ASSURANCE-CORRESPONDENCE-AUTHORIT-003 -->
Operational representations may exist in:

<!-- DP040-SINGLE-ASSURANCE-CORRESPONDENCE-AUTHORIT-004 -->
- correspondence records;
<!-- DP040-SINGLE-ASSURANCE-CORRESPONDENCE-AUTHORIT-005 -->
- governed-work metadata;
<!-- DP040-SINGLE-ASSURANCE-CORRESPONDENCE-AUTHORIT-006 -->
- review manifests;
<!-- DP040-SINGLE-ASSURANCE-CORRESPONDENCE-AUTHORIT-007 -->
- reviewer tooling;
<!-- DP040-SINGLE-ASSURANCE-CORRESPONDENCE-AUTHORIT-008 -->
- generated reports; and
<!-- DP040-SINGLE-ASSURANCE-CORRESPONDENCE-AUTHORIT-009 -->
- documentation.

<!-- DP040-SINGLE-ASSURANCE-CORRESPONDENCE-AUTHORIT-010 -->
Where multiple representations are required, they shall be generated from canonical correspondence or mechanically verified against it.

## Assurance Correspondence Integrity
<!-- section-id: ASSURANCE-CORRESPONDENCE-INTEGRITY -->

<!-- DP040-ASSURANCE-CORRESPONDENCE-INTEGRITY-001 -->
Canonical Assurance correspondence shall remain consistent with the maintained review-obligation graph.

<!-- DP040-ASSURANCE-CORRESPONDENCE-INTEGRITY-002 -->
Examples of defects include:

<!-- DP040-ASSURANCE-CORRESPONDENCE-INTEGRITY-003 -->
- `required` applicability with no review obligation;
<!-- DP040-ASSURANCE-CORRESPONDENCE-INTEGRITY-004 -->
- review obligation referencing unknown authority;
<!-- DP040-ASSURANCE-CORRESPONDENCE-INTEGRITY-005 -->
- review case referencing nonexistent obligations;
<!-- DP040-ASSURANCE-CORRESPONDENCE-INTEGRITY-006 -->
- finding with no review case;
<!-- DP040-ASSURANCE-CORRESPONDENCE-INTEGRITY-007 -->
- finding with no authority reference; and
<!-- DP040-ASSURANCE-CORRESPONDENCE-INTEGRITY-008 -->
- divergent duplicate mappings.

<!-- DP040-ASSURANCE-CORRESPONDENCE-INTEGRITY-009 -->
Objectively decidable integrity properties may themselves be mechanically enforced through Conformance.

## Generated Assurance Views
<!-- section-id: GENERATED-ASSURANCE-VIEWS -->

<!-- DP040-GENERATED-ASSURANCE-VIEWS-001 -->
Generated Assurance views may expose:

<!-- DP040-GENERATED-ASSURANCE-VIEWS-002 -->
- normative requirement identity;
<!-- DP040-GENERATED-ASSURANCE-VIEWS-003 -->
- Assurance applicability;
<!-- DP040-GENERATED-ASSURANCE-VIEWS-004 -->
- review obligations;
<!-- DP040-GENERATED-ASSURANCE-VIEWS-005 -->
- review cases;
<!-- DP040-GENERATED-ASSURANCE-VIEWS-006 -->
- findings;
<!-- DP040-GENERATED-ASSURANCE-VIEWS-007 -->
- unresolved ambiguity;
<!-- DP040-GENERATED-ASSURANCE-VIEWS-008 -->
- Governance routing; and
<!-- DP040-GENERATED-ASSURANCE-VIEWS-009 -->
- historical findings.

<!-- DP040-GENERATED-ASSURANCE-VIEWS-010 -->
Generated views remain subordinate derived artifacts.

<!-- DP040-GENERATED-ASSURANCE-VIEWS-011 -->
They do not independently establish semantic authority.

## Assurance Defects
<!-- section-id: ASSURANCE-DEFECTS -->

<!-- DP040-ASSURANCE-DEFECTS-001 -->
Examples of Assurance defects include:

<!-- DP040-ASSURANCE-DEFECTS-002 -->
- review obligation with no accepted authority;
<!-- DP040-ASSURANCE-DEFECTS-003 -->
- required review responsibility with no review obligation;
<!-- DP040-ASSURANCE-DEFECTS-004 -->
- review case with undefined scope;
<!-- DP040-ASSURANCE-DEFECTS-005 -->
- finding without evidence basis;
<!-- DP040-ASSURANCE-DEFECTS-006 -->
- finding without accepted authority;
<!-- DP040-ASSURANCE-DEFECTS-007 -->
- finding exceeding case scope;
<!-- DP040-ASSURANCE-DEFECTS-008 -->
- interpretation extending or narrowing accepted semantics;
<!-- DP040-ASSURANCE-DEFECTS-009 -->
- reviewer preference treated as authority;
<!-- DP040-ASSURANCE-DEFECTS-010 -->
- repeated findings treated as precedent without authorization;
<!-- DP040-ASSURANCE-DEFECTS-011 -->
- semantic review occurring outside the governed hierarchy;
<!-- DP040-ASSURANCE-DEFECTS-012 -->
- divergent correspondence mappings; and
<!-- DP040-ASSURANCE-DEFECTS-013 -->
- persistent ambiguity being silently resolved without Governance.

<!-- DP040-ASSURANCE-DEFECTS-014 -->
An Assurance defect shall not be repaired by inventing normative authority.

## Relationship to Governance
<!-- section-id: RELATIONSHIP-TO-GOVERNANCE -->

<!-- DP040-RELATIONSHIP-TO-GOVERNANCE-001 -->
Governance changes accepted normative authority.

<!-- DP040-RELATIONSHIP-TO-GOVERNANCE-002 -->
Assurance consumes accepted authority and produces semantic findings.

<!-- DP040-RELATIONSHIP-TO-GOVERNANCE-003 -->
Routing follows the responsibility owning the defect.

### Semantic Authority Defect
<!-- section-id: SEMANTIC-AUTHORITY-DEFECT -->

<!-- DP040-SEMANTIC-AUTHORITY-DEFECT-001 -->
**Assurance → Governance Design**

### Realization-Intent Defect
<!-- section-id: REALIZATION-INTENT-DEFECT -->

<!-- DP040-REALIZATION-INTENT-DEFECT-001 -->
**Assurance → Governance Plan**

<!-- DP040-REALIZATION-INTENT-DEFECT-002 -->
when accepted semantics remain sound.

### Realization Defect
<!-- section-id: REALIZATION-DEFECT -->

<!-- DP040-REALIZATION-DEFECT-001 -->
**Assurance → Governance Build**

<!-- DP040-REALIZATION-DEFECT-002 -->
when Design and Plan remain sound.

### Case-Specific Finding
<!-- section-id: CASE-SPECIFIC-FINDING -->

<!-- DP040-CASE-SPECIFIC-FINDING-001 -->
Return to the governed consumer or Governance stage requesting the review.

<!-- DP040-CASE-SPECIFIC-FINDING-002 -->
Governance determines persistent disposition.

## Relationship to Conformance
<!-- section-id: RELATIONSHIP-TO-CONFORMANCE -->

<!-- DP040-RELATIONSHIP-TO-CONFORMANCE-001 -->
Conformance establishes mechanically decidable facts.

<!-- DP040-RELATIONSHIP-TO-CONFORMANCE-002 -->
Assurance evaluates semantic matters requiring judgment.

<!-- DP040-RELATIONSHIP-TO-CONFORMANCE-003 -->
Assurance may conclude that Conformance:

<!-- DP040-RELATIONSHIP-TO-CONFORMANCE-004 -->
- faithfully represents authority;
<!-- DP040-RELATIONSHIP-TO-CONFORMANCE-005 -->
- over-enforces;
<!-- DP040-RELATIONSHIP-TO-CONFORMANCE-006 -->
- under-enforces;
<!-- DP040-RELATIONSHIP-TO-CONFORMANCE-007 -->
- incompletely represents authority;
<!-- DP040-RELATIONSHIP-TO-CONFORMANCE-008 -->
- uses semantically insufficient evidence; or
<!-- DP040-RELATIONSHIP-TO-CONFORMANCE-009 -->
- claims mechanical determinacy where ambiguity remains.

<!-- DP040-RELATIONSHIP-TO-CONFORMANCE-010 -->
Assurance shall not directly rewrite persistent Conformance semantics.

<!-- DP040-RELATIONSHIP-TO-CONFORMANCE-011 -->
Persistent correction routes through Governance.

## Candidate Assurance Requirements
<!-- section-id: CANDIDATE-ASSURANCE-REQUIREMENTS -->

<!-- DP040-CANDIDATE-ASSURANCE-REQUIREMENTS-001 -->
The following proposal-local statements are Design input. Their labels are non-normative; Planning may distill repository normative requirements from any combination of selected Design statements.

### ASSUR-01 — Governed Assurance Hierarchy
<!-- section-id: ASSUR-01-GOVERNED-ASSURANCE-HIERARCHY -->

<!-- DP040-ASSUR-01-GOVERNED-ASSURANCE-HIERARCHY-001 -->
**Governed semantic review and case-specific semantic judgment SHALL occur only through the authorized Assurance hierarchy.**

### ASSUR-02 — Assurance Provenance
<!-- section-id: ASSUR-02-ASSURANCE-PROVENANCE -->

<!-- DP040-ASSUR-02-ASSURANCE-PROVENANCE-001 -->
**Every maintained Assurance primitive SHALL resolve through governed provenance to accepted authority.**

### ASSUR-03 — Canonical Assurance Correspondence
<!-- section-id: ASSUR-03-CANONICAL-ASSURANCE-CORRESPONDE -->

<!-- DP040-ASSUR-03-CANONICAL-ASSURANCE-CORRESPONDE-001 -->
**Each active normative requirement SHALL have exactly one canonical Assurance correspondence record.**

### ASSUR-04 — Assurance Applicability
<!-- section-id: ASSUR-04-ASSURANCE-APPLICABILITY -->

<!-- DP040-ASSUR-04-ASSURANCE-APPLICABILITY-001 -->
**Each active normative requirement SHALL have exactly one canonical Assurance applicability determination.**

### ASSUR-05 — Required Review Coverage
<!-- section-id: ASSUR-05-REQUIRED-REVIEW-COVERAGE -->

<!-- DP040-ASSUR-05-REQUIRED-REVIEW-COVERAGE-001 -->
**Each normative requirement with required Assurance applicability SHALL resolve to at least one governed review obligation.**

### ASSUR-06 — Review Obligation Identity
<!-- section-id: ASSUR-06-REVIEW-OBLIGATION-IDENTITY -->

<!-- DP040-ASSUR-06-REVIEW-OBLIGATION-IDENTITY-001 -->
**Each maintained Assurance review obligation SHALL have a stable unique identity.**

### ASSUR-07 — Review Case Identity
<!-- section-id: ASSUR-07-REVIEW-CASE-IDENTITY -->

<!-- DP040-ASSUR-07-REVIEW-CASE-IDENTITY-001 -->
**Each governed Assurance review case SHALL have a stable unique identity.**

### ASSUR-08 — Review Case Scope
<!-- section-id: ASSUR-08-REVIEW-CASE-SCOPE -->

<!-- DP040-ASSUR-08-REVIEW-CASE-SCOPE-001 -->
**Each governed Assurance review case SHALL explicitly identify its authorizing authority, review obligations, and reviewed subject matter.**

### ASSUR-09 — Finding Identity
<!-- section-id: ASSUR-09-FINDING-IDENTITY -->

<!-- DP040-ASSUR-09-FINDING-IDENTITY-001 -->
**Each maintained Assurance finding SHALL have a stable identity within its review case.**

### ASSUR-10 — Finding Traceability
<!-- section-id: ASSUR-10-FINDING-TRACEABILITY -->

<!-- DP040-ASSUR-10-FINDING-TRACEABILITY-001 -->
**Each Assurance finding SHALL resolve to its review case, applicable review obligation, authorizing authority, reviewed subject matter, and evidence basis.**

### ASSUR-11 — Assurance Semantic Boundary
<!-- section-id: ASSUR-11-ASSURANCE-SEMANTIC-BOUNDARY -->

<!-- DP040-ASSUR-11-ASSURANCE-SEMANTIC-BOUNDARY-001 -->
**An Assurance finding SHALL NOT independently create, amend, supersede, withdraw, or establish persistent normative semantics beyond its authorized review case.**

### ASSUR-12 — Governance Routing
<!-- section-id: ASSUR-12-GOVERNANCE-ROUTING -->

<!-- DP040-ASSUR-12-GOVERNANCE-ROUTING-001 -->
**An Assurance finding requiring persistent normative semantic change SHALL route through Governance Design.**

### ASSUR-13 — Interpretation Boundary
<!-- section-id: ASSUR-13-INTERPRETATION-BOUNDARY -->

<!-- DP040-ASSUR-13-INTERPRETATION-BOUNDARY-001 -->
**Assurance interpretation SHALL remain within accepted normative semantics and SHALL NOT independently extend or narrow those semantics.**

### ASSUR-14 — Single Correspondence Authority
<!-- section-id: ASSUR-14-SINGLE-CORRESPONDENCE-AUTHORITY -->

<!-- DP040-ASSUR-14-SINGLE-CORRESPONDENCE-AUTHORITY-001 -->
**Requirement-to-Assurance correspondence SHALL NOT depend on independently maintained mappings that may silently diverge.**

### ASSUR-15 — Review Execution Closure
<!-- section-id: ASSUR-15-REVIEW-EXECUTION-CLOSURE -->

<!-- DP040-ASSUR-15-REVIEW-EXECUTION-CLOSURE-001 -->
**Each triggered Assurance review obligation SHALL be realized by a governed review case before the governed decision requiring that review may be accepted.**

## Primary Design Invariant
<!-- section-id: PRIMARY-DESIGN-INVARIANT -->

<!-- DP040-PRIMARY-DESIGN-INVARIANT-001 -->
**Assurance SHALL provide governed semantic review through a closed provenance model in which every maintained Assurance primitive derives from accepted authority, every triggered review obligation is realized by a traceable and explicitly scoped review case, every finding resolves to its authorizing authority, reviewed subject matter, and evidence basis, interpretation remains within accepted normative semantics, findings remain bounded to their authorized cases, and persistent semantic change returns through Governance.**

<!-- DP040-PRIMARY-DESIGN-INVARIANT-002 -->
All detailed Assurance design shall preserve this invariant.

## Audit Questions
<!-- section-id: AUDIT-QUESTIONS -->

<!-- DP040-AUDIT-QUESTIONS-001 -->
The current repository should be audited against this proposal by determining:

<!-- DP040-AUDIT-QUESTIONS-002 -->
1. Which current semantic review practices qualify as Assurance.

<!-- DP040-AUDIT-QUESTIONS-003 -->
2. Which semantic review practices exist only as informal convention.

<!-- DP040-AUDIT-QUESTIONS-004 -->
3. Which active normative requirements require Assurance responsibility.

<!-- DP040-AUDIT-QUESTIONS-005 -->
4. Which active normative requirements have no meaningful Assurance responsibility.

<!-- DP040-AUDIT-QUESTIONS-006 -->
5. Which existing `semantic-review` validation dispositions should become Assurance applicability.

<!-- DP040-AUDIT-QUESTIONS-007 -->
6. Which existing `partial` dispositions should become independent Conformance and Assurance relationships.

<!-- DP040-AUDIT-QUESTIONS-008 -->
7. Which review obligations currently have no accepted authority.

<!-- DP040-AUDIT-QUESTIONS-009 -->
8. Which required Assurance relationships have no identifiable review obligation.

<!-- DP040-AUDIT-QUESTIONS-010 -->
9. Which current reviews lack stable review-case identity.

<!-- DP040-AUDIT-QUESTIONS-011 -->
10. Which review cases lack explicit scope.

<!-- DP040-AUDIT-QUESTIONS-012 -->
11. Which findings lack stable identity.

<!-- DP040-AUDIT-QUESTIONS-013 -->
12. Which findings lack resolvable review obligations.

<!-- DP040-AUDIT-QUESTIONS-014 -->
13. Which findings lack resolvable normative authority.

<!-- DP040-AUDIT-QUESTIONS-015 -->
14. Which findings lack identifiable evidence basis.

<!-- DP040-AUDIT-QUESTIONS-016 -->
15. Which current findings exceed the semantic scope of their review cases.

<!-- DP040-AUDIT-QUESTIONS-017 -->
16. Which reviewer conclusions have become de facto persistent semantics without Governance.

<!-- DP040-AUDIT-QUESTIONS-018 -->
17. Which prior findings are being treated as precedent without accepted precedent authority.

<!-- DP040-AUDIT-QUESTIONS-019 -->
18. Which current semantic interpretations broaden or narrow accepted authority.

<!-- DP040-AUDIT-QUESTIONS-020 -->
19. Which current requirement-quality checks belong to Conformance because they are mechanically decidable.

<!-- DP040-AUDIT-QUESTIONS-021 -->
20. Which requirement-quality checks require Assurance judgment.

<!-- DP040-AUDIT-QUESTIONS-022 -->
21. Which current Conformance applicability decisions require Assurance review.

<!-- DP040-AUDIT-QUESTIONS-023 -->
22. Which current assertions may over-enforce or under-enforce accepted authority.

<!-- DP040-AUDIT-QUESTIONS-024 -->
23. Which mechanically complete evidence sets may remain semantically insufficient.

<!-- DP040-AUDIT-QUESTIONS-025 -->
24. Which Governance stage gates should require Assurance.

<!-- DP040-AUDIT-QUESTIONS-026 -->
25. Which Assurance correspondence mappings are duplicated across metadata, review tooling, templates, or generated documentation.

<!-- DP040-AUDIT-QUESTIONS-027 -->
26. Whether each candidate ASSUR requirement represents one independently identifiable obligation.

<!-- DP040-AUDIT-QUESTIONS-028 -->
27. Whether any candidate ASSUR requirement duplicates or logically follows from another.

<!-- DP040-AUDIT-QUESTIONS-029 -->
28. Which candidate ASSUR requirements can be structurally enforced through Conformance.

<!-- DP040-AUDIT-QUESTIONS-030 -->
29. What minimum Assurance authority must be accepted before Governance may require Assurance at Design, Plan, or Build acceptance.

## Explicitly Deferred Concerns
<!-- section-id: EXPLICITLY-DEFERRED-CONCERNS -->

<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-001 -->
The following concerns are intentionally outside this Assurance proposal:

<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-002 -->
- exact Assurance correspondence schema;
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-003 -->
- exact review-obligation schema;
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-004 -->
- exact review-case schema;
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-005 -->
- exact finding schema;
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-006 -->
- exact finding vocabulary;
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-007 -->
- exact reviewer-assignment rules;
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-008 -->
- exact reviewer cardinality;
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-009 -->
- exact reviewer-independence rules;
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-010 -->
- exact AI/human reviewer composition;
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-011 -->
- exact confidence representation;
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-012 -->
- exact semantic review rubrics;
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-013 -->
- exact evidence-manifest representation;
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-014 -->
- exact precedent model;
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-015 -->
- exact generated report format;
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-016 -->
- migration sequencing from current review practices; and
<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-017 -->
- bootstrap accommodations.

<!-- DP040-EXPLICITLY-DEFERRED-CONCERNS-018 -->
These concerns may be defined by subordinate Assurance authority during detailed Design and Plan.

## Relationship to the Framework
<!-- section-id: RELATIONSHIP-TO-THE-FRAMEWORK -->

<!-- DP040-RELATIONSHIP-TO-THE-FRAMEWORK-001 -->
The proposed framework model is:

<!-- DP040-RELATIONSHIP-TO-THE-FRAMEWORK-002 -->
**Framework Contract**  
<!-- DP040-RELATIONSHIP-TO-THE-FRAMEWORK-003 -->
→ defines authority topology

<!-- DP040-RELATIONSHIP-TO-THE-FRAMEWORK-004 -->
**Governance**  
<!-- DP040-RELATIONSHIP-TO-THE-FRAMEWORK-005 -->
→ controls persistent normative change

<!-- DP040-RELATIONSHIP-TO-THE-FRAMEWORK-006 -->
**Conformance**  
<!-- DP040-RELATIONSHIP-TO-THE-FRAMEWORK-007 -->
→ mechanically enforces accepted normative authority

<!-- DP040-RELATIONSHIP-TO-THE-FRAMEWORK-008 -->
**Assurance**  
<!-- DP040-RELATIONSHIP-TO-THE-FRAMEWORK-009 -->
→ performs governed semantic review and case-specific judgment

<!-- DP040-RELATIONSHIP-TO-THE-FRAMEWORK-010 -->
The three keystones interact without absorbing one another's powers.

<!-- DP040-RELATIONSHIP-TO-THE-FRAMEWORK-011 -->
Governance changes authority.

<!-- DP040-RELATIONSHIP-TO-THE-FRAMEWORK-012 -->
Conformance mechanically evaluates authority.

<!-- DP040-RELATIONSHIP-TO-THE-FRAMEWORK-013 -->
Assurance semantically evaluates authority, realization, and evidence.

<!-- DP040-RELATIONSHIP-TO-THE-FRAMEWORK-014 -->
Persistent semantic change returns through Governance.
