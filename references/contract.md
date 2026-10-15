# Project Contract

Child skills already follow [shared/vk-core-contract.md](../shared/vk-core-contract.md):
summary card, `./vk/<skill-key>/` records, git ignore `vk/`.

This file only covers **optional committed project context** in a product
repository. Do not use it as a replacement for a child skill or as a second
live checkpoint.

## Two directories (do not merge)

| Path | Git | Role |
| --- | --- | --- |
| `./vk/` | Ignore | Skill run records, checkpoints, bad cases. Never commit. |
| `./vank/context\|specs\|decisions\|status/` | Optional commit | Stable product constraints the team wants in the repo. |

Long-running resume lives in **one** file: `./vk/work/checkpoint.md`.
Do not duplicate live execution checkpoints under `./vank/status/`.
Canonical requirements own feature/acceptance status; canonical reviews own
finding status. The checkpoint links to them, without copying their ledgers.
Follow [document lifecycle](../shared/document-lifecycle.md) for revisions,
iterations, completion, acceptance, and repair history.

## Context layers

Use the closest reliable source first:

1. Repository instructions and existing project documentation.
2. Durable project context under `./vank/context/` if the team commits it.
3. Child-skill records under `./vk/` (read checkpoint, then confirm `HEAD`).
4. Current code and executable checks.

Treat code and checks as evidence when documentation disagrees. If the
checkpoint commit does not match `HEAD`, discard stale conclusions.

## Optional Vank directories

Create these only when a future reader needs them in git:

- `./vank/context/`: stable constraints and system boundaries.
- `./vank/specs/`: accepted task contracts beyond a one-off `vk-request` DSL.
- `./vank/decisions/`: durable trade-offs.

Ignore `vank/local/` if you generate scratch files there. Never change ignore
rules merely because an artifact was created.

## Result standard

Lead with the child skill's own contract. Additionally state:

- which child was selected and which were skipped;
- changed files or produced records;
- verification evidence;
- unresolved risks and the next decision.
