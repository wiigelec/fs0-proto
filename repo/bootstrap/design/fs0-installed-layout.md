# FS0 Repository-Structure Governance

## Status

Part of the non-authoritative FS0-Core Bootstrap Design Proposal.

Read `fs0-design.md` first. This chunk does not independently create authority.

---

# Purpose

This Design chunk defines only the methodology by which repository filesystem structure is authorized and mechanically evaluated.

It shall not define a concrete repository layout.

Concrete repository paths, directory trees, filenames, and repository-specific structural permissions belong exclusively to the canonical repository-structure configuration.

---

# Closed Repository Boundary

The repository root is the complete filesystem-structure governance boundary.

Every filesystem object beneath the repository root is subject to repository-structure governance.

No filesystem object is exempt because it is version-control state, ignored state, generated state, cached state, temporary state, editor state, build output, tool output, runtime state, or otherwise conventionally treated as incidental.

A filesystem object may exist only when positive structural authorization applies.

Absence of applicable authorization means deny.

---

# Canonical Structural Permission Source

Exactly one canonical repository-structure configuration shall govern filesystem permission for the repository.

That configuration is the sole instance-level source of permission for filesystem objects beneath the repository root.

Design defines the semantics of structural authorization.

Configuration defines the concrete repository structure authorized under those semantics.

Implementation, source-code defaults, generated output lists, version-control ignore rules, workflow conventions, historical presence, or successful prior validation shall not independently authorize filesystem structure.

The canonical configuration shall itself be subject to repository-structure authorization.

## Configuration Resolution

The operating substrate shall present exactly one candidate repository-structure configuration identity to Conformance through a location-independent resolution mechanism.

The mechanism shall identify which configuration is canonical for the validation operation without granting permission to the filesystem object that carries it.

After loading the configuration, Conformance shall require that the configuration's own filesystem object is positively authorized by that configuration.

Failure to resolve exactly one candidate configuration shall fail repository-structure Conformance.

No fixed filesystem path, implicit filename, search order, or implementation fallback may substitute for canonical resolution.

---

# Structural Authorization Semantics

FS0 shall support authorization of files and directories.

An authorization may distinguish required presence from permitted presence.

A required object shall cause Conformance failure when absent.

A permitted object may be absent without causing failure.

A present object without applicable authorization shall cause Conformance failure.

Directory authorization shall be closed by default.

Authorizing a directory shall authorize that directory object only.

Its descendants shall require additional applicable authorization unless the directory authorization explicitly grants complete-subtree permission.

Complete-subtree permission shall authorize descendant filesystem objects without requiring additional structural configuration for those descendants.

Complete-subtree permission remains positive authorization and shall not be treated as an ungoverned exception.

FS0 structural authorization shall explicitly distinguish ordinary files, directories, and symbolic links.

An object type unsupported by the canonical configuration semantics shall be denied by default.

A symbolic link shall be authorized as the link object itself.

Structural traversal shall not follow a symbolic-link target to discover descendants.

A symbolic-link target outside the repository root shall not enlarge the repository-structure governance boundary.

---

# Structural Resolution

For every observed filesystem object beneath the repository root, Conformance shall resolve applicable structural authorization.

Resolution shall produce one of two outcomes:

```text
authorized
denied
```

No implicit, ignored, unknown, or outside-scope structural outcome exists beneath the repository root.

For every configuration entry requiring presence, Conformance shall verify that the required object exists.

Repository-structure closure therefore requires both:

```text
observed object -> authorization
required authorization -> observed object
```

---

# Bootstrap Methodology

Before the first FS0 candidate exists, repository construction occurs under the explicit external bootstrap boundary defined by FS0 Bootstrap Design.

Bootstrap shall establish a canonical repository-structure configuration as part of constructing the candidate FS0 state.

The candidate shall not be conforming merely because bootstrap created its files.

Before candidate acceptance, Conformance shall evaluate the complete filesystem namespace beneath the repository root against the candidate configuration.

After candidate construction, no bootstrap convention, hard-coded implementation path, generator destination list, or tool-specific default may substitute for structural authorization.

---

# Design / Configuration / Implementation Separation

The layers are:

```text
Design
  defines structural governance methodology and authorization semantics

Configuration
  defines concrete repository filesystem permissions

Implementation
  evaluates the actual filesystem against configuration
```

Design shall not enumerate repository-specific filesystem structure.

Configuration shall not redefine the governing methodology.

Implementation shall not invent structural permission absent from configuration.

---

# Minimum Conformance Obligations

At minimum, repository-structure Conformance shall verify that:

- exactly one canonical repository-structure configuration is resolved without relying on a fixed filesystem path or implicit search convention;
- the resolved configuration authorizes its own filesystem object;
- every filesystem object beneath repository root has applicable positive authorization;
- every required configured object exists;
- directory descendants are denied unless individually authorized or covered by explicit complete-subtree authorization;
- no implicit exemptions are applied;
- the configuration itself is authorized;
- filesystem evaluation is performed against the actual repository-root namespace; and
- validation failure identifies unauthorized or missing objects sufficiently for correction.

---

# Deferred Structure Features

FS0 may defer richer repository-structure capabilities not required for the initial closed-repository model, including advanced pattern languages, reusable profiles, conditional policies, structural inheritance, generalized artifact taxonomy, and richer classification systems.

Deferral of those capabilities shall not weaken the FS0 invariant that every filesystem object beneath repository root requires positive authorization.
