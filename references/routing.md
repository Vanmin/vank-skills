# Routing

This package is a one-install suite with many child skills.
After choosing a row, read that child's `SKILL.md` and execute it. Do not
improvise from this table.

## Choose a child

| User intent | Load | Typical output |
| --- | --- | --- |
| Explain a concept, clarify a decision, trade-off Q&A | `vk-question/SKILL.md` | Structured answer + optional `./vk/question/` note |
| Trace a code path without editing | `vk-read/SKILL.md` | Evidence-backed reading record |
| Map a repo or subdirectory | `vk-roadmap/SKILL.md` | `./vk/roadmap/` document |
| Turn intent into an executable DSL / spec | `vk-request/SKILL.md` | DSL under `./vk/request/` |
| Backend design: DB, cache, RPC, MQ, lock, To-C | `vk-restrict/SKILL.md` | Three-axis constraints |
| Backend application business-layer implementation quality | `vk-backend-quality/SKILL.md` | Per-slice layer, error, type, reuse, and structure gates |
| Implement, fix, refactor, long-running delivery | `vk-work/SKILL.md` | Scoped change + `./vk/work/` record |
| Test, retest, process acceptance or acceptance feedback | `vk-work/SKILL.md` | Updated canonical requirement ledger and phase gate result |
| Review a diff, risk, regression | `vk-review/SKILL.md` | Findings and verdict |
| Prepare commit, push, `vkpush` | `vk-submit/SKILL.md` | Scope-checked handoff |
| WeChat / long-form article package | `vk-writer/SKILL.md` | Outline, style, draft |
| iOS / SwiftUI multi-skill delivery | `vk-ios-agents/SKILL.md` | Orchestrated iOS plan |
| Broken or clipped diagrams | `vk-diagram-guard/SKILL.md` | Gate report + repaired assets |
| Sync local articles to Lark / Feishu | `vk-write-lark/SKILL.md` | Inventory, blockers, sync plan |
| Clean, audit, or sync this skill suite | `vk-skill-man/SKILL.md` | Maintenance log |
| User named `$vank` but the task is still unclear | this router | Ask once, then pick a child |

If the user already named a child (`$vk-work`, `/vk-review`, …), skip this
table and load that skill directly.

## Sequence

For a request with multiple intents, use this order and skip finished phases:

```text
question/read/roadmap → request → restrict → work → review → submit
```

`vk-backend-quality` is normally loaded by `vk-work` during backend application
implementation and by `vk-review` for the final diff check. Do not route simple
scripts or tooling changes through it.

Specialists (`vk-writer`, `vk-ios-agents`, `vk-diagram-guard`,
`vk-write-lark`) are additive only when that domain is present.

For functional work the delivery stages are confirmation -> development ->
testing -> acceptance -> completion, owned by `vk-work` with the canonical
requirement ledger. Problems in any stage return through recorded repair or
scope adjustment -> retesting -> reacceptance. See
[delivery workflow](../shared/delivery-workflow.md). Skill invocation order
does not itself prove delivery completion; submission is independent.

## gstack bridge for implementation

For non-trivial implementation, `vk-work` owns the lifecycle. After local
verification, it may read [gstack bridge](gstack-bridge.md) only when a
bridge entry criterion matches. It does not run gstack wholesale, does not
use gstack `benchmark` as backend capacity evidence, and does not let gstack
`qa` commit.

## Compatibility

- Child skills still invoke each other by relative path
  (`../vk-restrict/SKILL.md`, `../shared/vk-core-contract.md`).
- Default install is one `vank` directory. Nested `name: vk-*` children
  stay independently invocable (`$vk-work`) when the host recurses, the
  same way gstack exposes `/review` from `gstack/review`.
- If a host only scans one directory level, re-run
  `bash scripts/install.sh --with-shims`.
- `$vk-work` and `$vank` are both valid. `$vank` only routes; `$vk-work`
  executes.
- If `$vk-work` is missing after install, the host likely does not recurse
  into nested `SKILL.md` files. Re-run `bash scripts/install.sh --with-shims`.
