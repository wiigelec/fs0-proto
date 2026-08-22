# FS0 Operating Substrate

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
        ├── templates/
        └── scripts/
```

Before bootstrap execution, this payload is only bootstrap construction state.

The initial FS0 Design Proposal belongs at:

```text
repo/bootstrap/design/fs0-design.md
```

Canonical bootstrap templates belong at:

```text
repo/bootstrap/templates/
```

Bootstrap construction scripts belong at:

```text
repo/bootstrap/scripts/
```

The canonical bootstrap entry point is the executable shell wrapper:

```text
repo/bootstrap/scripts/bootstrap
```

It shall be invoked from the target repository root as:

```bash
./repo/bootstrap/scripts/bootstrap
```

The wrapper shall remain thin.

Its responsibilities are limited to invocation concerns such as validating repository-root execution context, resolving its own implementation path, and delegating to the substantive bootstrap implementation.

All substantive bootstrap implementation shall live under:

```text
repo/bootstrap/scripts/src/
```

`scripts/bootstrap` defines invocation.

`scripts/src/` defines implementation.

These bootstrap paths are retained FS0 maintenance-source and generation surfaces after cutover.

They do not gain normative authority from that role.

Their retention does not require later functional sets or the final successor framework to use the same namespace or mechanism.

---

---

# Bootstrap Principle

FS0 cannot authorize its own initial existence.

Therefore one explicit external bootstrap exception is required.

Before cutover, the bootstrap process operates outside FS0 Governance authority.

Pre-cutover execution of candidate FS0 mechanisms produces bootstrap verification evidence only.

It shall not be represented as governed FS0 Conformance, governed FS0 Assurance, or FS0 Governance acceptance before the first FS0 state is accepted.

The bootstrap mechanism may:

- construct the initial FS0 candidate inside a user-supplied Git repository;
- install the minimum FS0 GitHub operating profile into repository content;
- publish and inspect candidate state through the user-established Git/GitHub environment;
- run initial bootstrap mechanical verification;
- run external bootstrap semantic audit;
- correct bootstrap defects; and
- explicitly accept one exact repository revision as the first FS0 operating state.

After initial FS0 acceptance, bootstrap authority is exhausted.

Bootstrap maintenance machinery may remain in use for FS0 maintenance.

Its execution shall not independently authorize mutation or create accepted state.

All subsequent persistent framework change shall occur through FS0 Governance.

---

---

## User-Supplied Git and GitHub Prerequisites

The bootstrap implementation shall not initialize the target Git repository, create the GitHub repository, or establish user credentials.

Before bootstrap begins, the user is responsible for providing:

```text
target repository path
initialized Git repository
configured GitHub remote
existing GitHub repository
working Git authentication
working GitHub API authentication
required network connectivity
```

Bootstrap shall verify these prerequisites before mutation.

A missing prerequisite shall stop bootstrap with a clear error.

Bootstrap shall not silently create repositories, manufacture credentials, or substitute an ungoverned manual path.

Git and GitHub presence are external operating prerequisites.

Their existence does not create FS0 authority.

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

## Bootstrap-Generated Repository Orientation Surfaces

The bootstrap implementation shall generate the following files in the root of the installed FS0 repository:

```text
README.md
AGENTS.md
LICENSE
```

## Bootstrap Output Generation Rule

`README.md`, `AGENTS.md`, and `LICENSE` are installed FS0 outputs.

They are not files that belong in the `fs0-proto` source root and they are not prerequisites for running the bootstrap implementation.

A clean bootstrap run against a compliant target repository that lacks these files shall create them.

Their contents shall be deterministic for the same bootstrap Design and canonical bootstrap implementation revision, except for explicitly variable installation-state fields.

Bootstrap verification shall fail if any required generated root surface is absent.

After cutover, later modifications to these maintained files shall occur only through FS0 Governance.

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

## Bootstrap Payload Scope

`repo/bootstrap/` shall contain only material required to construct, verify, accept, and cut over FS0.

Its allowed source roles are:

```text
design/     non-authoritative bootstrap Design input
templates/  canonical bootstrap realization inputs
scripts/    canonical shell entry point plus bootstrap implementation under `scripts/src/`
```

Generated artifacts shall not be written under `repo/bootstrap/`.

The bootstrap payload shall not contain requirements, design discussion, or implementation assumptions for the future developed repo-spec product except where strictly necessary to define the bootstrap output required for FS0 self-hosting.

The shell wrapper shall contain no substantive bootstrap semantics. Substantive transformation, validation, installation, verification, and cutover logic shall live under `repo/bootstrap/scripts/src/` and shall not embed successor semantics that belong in canonical template input.

After `repo/bootstrap/` is present in a compliant target repository, bootstrap shall require no semantic, template, or script input from the originating repository.

## Bootstrap Data, Template, and Generator Model

For bootstrap-created maintained artifacts, the canonical maintenance model is:

```text
structured source data
+ layout template
+ generator
→ generated artifact outside repo/bootstrap/
```

Each generated artifact shall have a machine-resolvable source definition identifying its canonical source data, applicable template or layout, generator, and generated destination.

The same general model shall be used for the complete successor repo-spec Design Proposal seed set.

Generated artifacts are read or operating surfaces and shall not become independent maintenance sources.

## Bootstrap Template Source Tree

The canonical bootstrap template source tree shall be:

```text
repo/bootstrap/templates/
|-- fs0/
|   |-- authority/
|   |-- requirements/
|   |-- conformance/
|   |-- assurance/
|   |-- orientation/
|   `-- github/
`-- proposals/
    |-- index.json
    `-- <proposal-id>/
        |-- proposal.json
        `-- chunks/
            `-- <ordered-chunk>.json
```

`templates/fs0/` contains canonical structured inputs used to construct the initial FS0 candidate.

`templates/proposals/` contains canonical structured non-authoritative successor Design Proposal inputs.

The two classes shall remain distinct because their authority status differs:

```text
templates/fs0/        bootstrap realization input for initial accepted FS0 candidate
templates/proposals/  non-authoritative seed input for later FS0 Governance Design
```

Template content shall be structured and machine-resolvable.

Generated Markdown shall not be stored under `repo/bootstrap/templates/`.

## Bootstrap Script Layout

The bootstrap script tree shall be:

```text
repo/bootstrap/scripts/
|-- bootstrap
`-- src/
    `-- ...
```

`bootstrap` shall be a shell script with an executable bit and a shell shebang.

It is the only canonical bootstrap invocation surface.

Substantive implementation files shall be located under `src/`.

Implementation language and internal module structure may evolve during realization so long as the canonical entry point and wrapper/implementation separation remain unchanged.

## Bootstrap Independence

After cutover, authoritative determination shall not require reading `repo/bootstrap/`.

FS0 maintenance may use the accepted repository's retained bootstrap source and generation machinery when authorized by FS0 Governance.

Post-cutover operation shall require no semantic, template, generator, or script input from the originating bootstrap repository or another external bootstrap environment.

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
