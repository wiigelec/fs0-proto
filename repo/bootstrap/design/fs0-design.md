# FS0-Core Bootstrap Design Proposal

## Status

Design proposal for the disposable `fs0-proto` bootstrap repository.

This document is non-authoritative bootstrap Design input.

It does not become accepted FS0 authority before cutover.

The one-time external bootstrap process may use this Design input to construct, audit, verify, and explicitly accept the first FS0 operating state.

Its purpose is to define the minimum end-to-end functional set required to install a self-hosting repository framework that can use its own Governance, Conformance, Assurance, operating substrate, and GitHub mechanisms to build the remainder of the successor repo-spec design.

FS0 is intentionally minimal.

Anything FS0 can correctly build after bootstrap should be deferred unless it is required for the first complete self-hosted remote lifecycle.

---

# Design Proposal Structure

This Design Proposal is split into bounded chunks so a human or AI agent can load only the context required for the current question.

The chunks collectively form one non-authoritative FS0 Design Proposal. No chunk independently creates authority.

| File | Primary content |
| --- | --- |
| `fs0-design.md` | entry point, objective, invariant, capability map |
| `fs0-authority-governance.md` | acceptance state, authority, Governance, normative requirements |
| `fs0-conformance-assurance.md` | mechanical Conformance and semantic Assurance kernels |
| `fs0-operating-substrate.md` | bootstrap boundary, user prerequisites, operating substrate, bootstrap implementation |
| `fs0-github.md` | GitHub capability contract, fixed GitHub binding, cutover |
| `fs0-installed-layout.md` | concrete installed FS0 tree and structure enforcement |
| `fs0-self-hosting.md` | installed state, exclusions, self-hosting demonstration, acceptance and audit |

## Loading Rule

Always read this index first.

Then load only the chunk or chunks relevant to the current operation. Cross-cutting audits may load all chunks.

---

# Objective

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

---

# Primary Design Invariant

**FS0 SHALL be the smallest self-sufficient network-capable framework kernel able to govern, modify, evaluate, and publish itself after cutover, and every capability not required for the first successful FS0-governed construction and acceptance of FS1 SHALL be deferred.**

---

---

# FS0 Capability Set

FS0 consists of eight capability groups:

1. Authority Kernel
2. Governance Kernel
3. Normative Requirement Kernel
4. Conformance Kernel
5. Assurance Kernel
6. Operating Substrate
7. GitHub Remote Operating Profile
8. Bootstrap Installation and Cutover

These groups are capability boundaries, not necessarily final specification or directory boundaries.

---

# FS0 Maintenance and Read-Surface Boundary

`repo/bootstrap/` is the canonical non-authoritative maintenance source and generation implementation for FS0.

After cutover, authoritative determination shall use accepted read surfaces outside `repo/bootstrap/`.

Bootstrap source shall not become fallback authority when source and generated read surfaces disagree.

Post-cutover FS0 maintenance may modify bootstrap source only through FS0 Governance-authorized work.

Generated FS0 read surfaces shall be produced from canonical bootstrap data, templates, and generators.

Generated FS0 read surfaces shall not be independently maintained as canonical source.

Generation shall be deterministic for identical canonical inputs and explicitly declared variable inputs.

Conformance shall mechanically verify correspondence between canonical bootstrap source and generated FS0 read surfaces.

A source/read-surface mismatch is a Conformance defect.

Post-cutover FS0 shall require no semantic, template, generator, or script input from outside the accepted repository state.

---
