# Routing

This package is a one-install suite with many child skills.
After choosing a row, read that child's `SKILL.md` and execute it. Do not
improvise from this table.

## Choose a child

| User intent | Load | Typical output |
| --- | --- | --- |
| Explain a concept, clarify a decision, Chinese Q&A | `vk-question/SKILL.md` | Structured answer + optional `./vk/question/` note |
| Trace a code path without editing | `vk-read/SKILL.md` | Evidence-backed reading record |
| Map a repo or subdirectory | `vk-roadmap/SKILL.md` | `./vk/roadmap/` document |
| Turn intent into an executable DSL / spec | `vk-request/SKILL.md` | DSL under `./vk/request/` |
| Backend design: DB, cache, RPC, MQ, lock, To-C | `vk-restrict/SKILL.md` | Three-axis constraints |
| Implement, fix, refactor, long-running delivery | `vk-work/SKILL.md` | Scoped change + `./vk/work/` record |
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

Specialists (`vk-writer`, `vk-ios-agents`, `vk-diagram-guard`,
`vk-write-lark`) are additive only when that domain is present.

## gstack bridge for implementation

For non-trivial implementation, `vk-work` owns the lifecycle and reads
[gstack bridge](gstack-bridge.md). It selects an installed gstack specialist
only when the task needs browser QA, performance evidence, security review,
or an authorized release. It does not run gstack wholesale and it does not
duplicate Vank's backend gate, review record, or submission safety checks.

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
