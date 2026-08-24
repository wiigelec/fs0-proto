# Agent Instructions

This file provides operational guidance for AI and automated agents working in an FS0 repository. It is not normative authority.


## Initial reading order

1. Read `repo/state/bootstrap.json` to determine bootstrap/cutover state.
2. Read the applicable normative authority under `repo/authority/`.
3. Use `repo/proposals/registry.json` to discover installed successor Design Proposals and their canonical structured read representations.
4. Use `repo/bootstrap/design/` only for bootstrap Design-chunk discovery and maintenance context; it is not post-cutover authority.
5. After publication, resolve accepted state through `refs/heads/accepted` together with the immutable receipt tag `refs/tags/fs0-acceptance/<accepted-sha>`.

## Authority

- Technical write capability is not authority.
- Read the applicable records under `repo/authority/` before interpreting normative requirements.
- Do not treat `README.md`, `AGENTS.md`, implementation code, generated output, workflow state, issue state, merge state, or the default branch as independent normative authority.
- Do not infer that one repository or GitHub state class has another state class's semantics merely because the states coincide.
- A merge, issue closure, CI success, or agent declaration does not itself create acceptance.

## Mutation

- Before mutation, inspect the exact candidate, applicable authority, authorization, and available evidence.
- Keep mutations bounded to their authorization.
- After cutover, persistent framework mutation must route through Governance.
- Do not directly maintain generated FS0 surfaces. Modify their canonical maintained source only when authorized, regenerate, and validate.
- `repo/bootstrap/data/` is retained maintenance source; after cutover it is not an authoritative read surface.

## Working with requirements

- Prefer bounded context. Read `repo/bootstrap/data/model.json`, the relevant authority metadata, and only the requirement chunk needed for the task.
- Preserve stable requirement identity and authority ownership.
- Do not add semantic policy to generator code when it belongs in bootstrap data or accepted authority.
- Do not compress or omit material normative semantics merely to reduce file or context size.

## Verification

Run the canonical validation interface from the repository root:

```bash
./repo/scripts/validate
```

Use `--verbose` for assertion detail and `--json` for the complete structured result.

Treat an incomplete result as incomplete. Do not report pending assertions as conforming.
