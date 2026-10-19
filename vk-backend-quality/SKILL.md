---
name: vk-backend-quality
description: Enforce backend application service-layer quality during each code slice: business boundaries, readable code, cognitive complexity, typed errors and states, reuse, structure, and safe simplification. Excludes simple scripts and tooling.
---

# vk-backend-quality

This skill is a backend application business-layer implementation gate. It is
designed to run while a service feature is being written, before the next slice and
before testing handoff. It can also review an existing service diff when explicitly
invoked.

## Shared contract

- Load `../shared/vk-core-contract.md` before acting.
- Load `../shared/backend-business-quality.md` for the rules and severity model.
- Load `references/code-quality-rules.md` for authoring, review, and simplification
  guidance. Read only the sections relevant to the current code.
- Local records go under `./vk/backend-quality/` only when the shared selective
  record policy warrants them.
- Follow the shared result contract. Routine per-slice checks may report inline;
  material findings or a reusable baseline may create a local record.

## When to run

Run automatically from `vk-work` when the change touches a backend application's
handler/transport, service/usecase, domain state, repository, API error code,
status/message, transaction, or business side effect. A production worker, cron job,
or message consumer also qualifies when it changes domain state or invokes the same
business service boundary.

Do not load this skill for simple scripts, one-off utilities, build/release scripts,
test fixtures, migrations without business-layer code, pure configuration, frontend,
copy, rename, or read-only work. A script that becomes a production business
workflow qualifies only when it owns or changes the domain behavior described above.

## Workflow

1. Read the current diff and repository instructions. Identify the local layer names,
   feature file shape, response envelope, error type, and test conventions.
2. Before implementing a slice, state its business contract: preconditions, state
   changes, domain errors, transport mapping, side effects, and idempotency when
   relevant. Mark unknowns as `TBD` or `ASSUMPTION:`.
3. Implement the smallest slice inside the existing architecture, applying the
   relevant rules from `references/code-quality-rules.md` while writing it. Keep
   quality decisions visible in the code and checks instead of narrating every
   stylistic choice.
4. Apply the per-slice business and code-quality gates from
   `../shared/backend-business-quality.md` and the code-quality reference.
5. Fix blocking findings and concrete repair findings before starting the next slice.
   Keep repair scope limited
   to the current feature unless a shared boundary is demonstrably affected.
6. Run targeted service, repository, and transport contract tests before testing
   handoff. Reuse valid evidence and broaden only for a concrete risk.
7. If the implementation needs cleanup, apply the bounded simplification procedure
   only after targeted checks pass. Recheck the final diff and preserve behavior.
8. Report findings with rule IDs, locations, severity, correction direction, and
   retest evidence.

## Relationship to other skills

- `vk-work` owns the implementation loop and must load this gate before coding.
- `vk-restrict` owns backend data flow, IO, concurrency, abuse prevention, and
  dependency constraints. Load it when those boundaries are involved.
- `vk-review` performs the final independent recheck; its approval does not replace
  business acceptance.

## Hard rules

- Never allow SQL/ORM/driver errors or `err.Error()` to reach a client response.
- Never let handlers own SQL, repository implementation details, or business state
  transitions.
- Never let services write transport status, JSON, or protocol envelopes.
- Use a centralized mapping for domain error code, transport status, and safe message.
- Use named types/constants for finite states and shared protocol values.
- Keep functions linear and single-purpose; report concrete complexity or mixed
  abstraction problems rather than enforcing arbitrary line limits.
- Search before adding helpers, constants, mappings, or packages.
- Keep business decisions separate from database, RPC, clock, ID, and serialization
  side effects where practical.
- Preserve the repository's existing file structure; do not introduce a parallel
  architecture for one feature.
- Do not add a helper or constant solely to satisfy a style preference; tie it to
  real reuse, a shared contract, or a boundary.
