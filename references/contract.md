# Project Contract

Child skills already follow [shared/vk-core-contract.md](../shared/vk-core-contract.md):
summary card, `./vk/<skill-key>/` records, git ignore `vk/`.

This file only covers **optional project context** in a product repository.
Do not use it as a replacement for a child skill.

## Context layers

Use the closest reliable source first:

1. Repository instructions and existing project documentation.
2. Durable project context under `./vank/context/`, if the team commits it.
3. Child-skill records under `./vk/`.
4. Current code and executable checks.

Treat code and checks as evidence when documentation disagrees.

## Optional Vank directories

Create these only when a future reader needs them:

- `./vank/context/`: stable constraints and system boundaries.
- `./vank/specs/`: accepted task contracts beyond a one-off `vk-request` DSL.
- `./vank/decisions/`: durable trade-offs.
- `./vank/status/`: compact resumable handoff for a long task.

Ignore `vank/local/` if you generate scratch files there. Never change ignore
rules merely because an artifact was created.

## Result standard

Lead with the child skill's own contract. Additionally state:

- which child was selected and which were skipped;
- changed files or produced records;
- verification evidence;
- unresolved risks and the next decision.
