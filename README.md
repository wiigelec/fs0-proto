# fs0-proto

Disposable bootstrap prototype for FS0-Core, the minimal self-hosting kernel for the successor repo-spec architecture.

## Current status

This repository is in **pre-cutover bootstrap construction**.

Nothing in the prototype becomes accepted FS0 authority merely because it is committed, merged, executable, or present on GitHub.

The external bootstrap process is being used to construct and audit the first candidate FS0 state. After cutover, persistent framework evolution must route through FS0 Governance.

## Design entry point

Start with:

`repo/bootstrap/design/fs0-design.md`

That file is the Design Proposal index and tells you which bounded design chunk to load next.

## Operating model

FS0 is intended to be like a minimal base operating-system installation: small but self-sufficient.

After cutover it must have enough Governance, Conformance, Assurance, Git, networking, authenticated GitHub access, remote execution, and bounded privileged-mutation capability to build the rest of the framework without the external bootstrap environment.

## Accepted state

Before cutover there is no FS0-governed accepted state.

After cutover, accepted repository state is resolved through the dedicated `accepted` Git ref plus its matching explicit acceptance record. Default-branch position alone does not create acceptance.

## Agent guidance

AI agents and automated contributors must read `AGENTS.md` before mutation.

## License

GNU General Public License version 3. See `LICENSE`.
