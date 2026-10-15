# vk-work references

Load files from **this directory** (the `vk-work` skill folder), never from
`$HOME/.codex/skills/vk-work/...`.

| File | Load when |
| --- | --- |
| `verification-matrix.md` | `standard` or `high-risk` backend behavior change |
| `workflow.md` | `standard` or `high-risk` (detailed steps) |
| `../../shared/delivery-workflow.md` | Functional delivery, tests/retests, acceptance feedback, phase handoff |
| `long-running.md` | Multi-module / multi-cycle / user asked for subagents |
| `{language}/README.md` | That file exists next to this index (`swift/README.md` for Apple) |

If `references/{language}/` is missing, stay in fallback: repository
conventions and language-native checks. Absence must not block the task.
Do not invent framework rules.

`../references/gstack-bridge.md` (package-level) loads only after local
verification on a non-trivial change whose bridge entry criteria match.
