# FS0 Conformance and Assurance

## Status

Part of the non-authoritative FS0-Core Bootstrap Design Proposal.

Read `fs0-design.md` first. This chunk does not independently create authority.

---

# FS0.4 — Conformance Kernel

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

Local execution may exist as an implementation convenience.

Before cutover, the candidate remote execution surface shall run in GitHub Actions as bootstrap mechanical verification evidence.

After cutover, that accepted execution surface becomes canonical FS0 Conformance execution unless later changed through Governance.

---

---

# FS0.5 — Assurance Kernel

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
