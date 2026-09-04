---
name: vank
description: Router for the Vank skill suite. Install once to get the full vk workflow set. Use when the user invokes vank, asks which vk skill to use, or wants question/read/roadmap/request/restrict/work/review/submit/writer/iOS/diagram/Lark/skill-man workflows without naming a child skill.
---

# Vank

Human docs: [README.md](README.md) (English), [README.zh-CN.md](README.zh-CN.md) (Chinese).

Vank is one installable package. Nested `vk-*` directories are the real
skills. This file only chooses which child skill to run, then follows that
skill in full. Do not substitute the routing table for a child `SKILL.md`.

## Start

1. Identify the outcome. If the user already named a child skill
   (`$vk-work`, `/vk-request`, …), read that child `SKILL.md` and stop routing.
2. Read [routing](references/routing.md) and pick the smallest matching child.
3. Read [shared/vk-core-contract.md](shared/vk-core-contract.md), then read the
   chosen child `SKILL.md`. Execute that skill as written, including its
   record directory under `./vk/<skill-key>/`. For non-trivial implementation,
   `vk-work` also applies the optional [gstack bridge](references/gstack-bridge.md).
4. Load extra children only when the chosen skill says so (for example
   `vk-work` loading `vk-restrict`).
5. Report the selected skill, skipped children, and the child skill's own
   result contract.

## Children

| Intent | Skill |
| --- | --- |
| Concept, Q&A, trade-offs | [vk-question](vk-question/SKILL.md) |
| Read-only code tracing | [vk-read](vk-read/SKILL.md) |
| Repository / module map | [vk-roadmap](vk-roadmap/SKILL.md) |
| Requirements → executable DSL | [vk-request](vk-request/SKILL.md) |
| Backend data / IO / dependency gates | [vk-restrict](vk-restrict/SKILL.md) |
| Implement, repair, long-running delivery | [vk-work](vk-work/SKILL.md) |
| Diff review and risk | [vk-review](vk-review/SKILL.md) |
| Commit, push, release handoff | [vk-submit](vk-submit/SKILL.md) |
| Long-form article package | [vk-writer](vk-writer/SKILL.md) |
| iOS multi-skill orchestration | [vk-ios-agents](vk-ios-agents/SKILL.md) |
| Diagram asset gate and repair | [vk-diagram-guard](vk-diagram-guard/SKILL.md) |
| Local docs → Lark/Feishu plan | [vk-write-lark](vk-write-lark/SKILL.md) |
| Maintain this package / local skill hygiene | [vk-skill-man](vk-skill-man/SKILL.md) |

Optional project-level context (not a substitute for `./vk/` records):
[contract](references/contract.md). Package install and evolution:
[governance](references/governance.md).

## Boundaries

- Do not flatten children into 13 separately maintained packages.
- Do not run every child. Skip phases the user already finished.
- Do not copy or fork gstack. When its installed specialist skills are useful,
  invoke them through the bridge and keep Vank as the project-record owner.
- Do not commit, push, deploy, or write to cloud docs unless the child skill
  and the user both authorize it.
- Keep durable product context in the target repository when the team wants
  to share it. Keep skill run records under that repository's `./vk/`.
