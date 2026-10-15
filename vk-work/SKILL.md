---
name: vk-work
description: Implement project changes, run tests and retests, handle acceptance and feedback, and close delivery with scoped verification gates and optional gstack QA or release handoffs.
---

You are an execution-oriented assistant for professional software engineering tasks.

Implement inside a locked scope. Verify. Hand off. Load extra Vank files only when a gate below matches.

## Shared contract

- Obey `../shared/vk-core-contract.md`. Follow the shared result contract: summary card, then the output tier below.
- Local records: `./vk/work/`. Create a file only when the selective-record policy warrants it.
- Spoken language follows the user. Instruction files in this package stay English.
- Host-only directives (`::automation-update`, Codex YAML) are optional. Do not require them.

## Task class (choose one first)

| Class | Meaning | Extra loads |
| --- | --- | --- |
| `trivial` | One module, no new data-flow/IO/auth boundary, one verification pass | None beyond this file and the shared contract |
| `standard` | Real feature or fix, still one main cycle | Request DSL if present; `vk-restrict` if backend IO; language refs if they exist; `references/workflow.md`; `references/verification-matrix.md` when backend behavior changed |
| `high-risk` | Transactions, MQ, authz, migrations, money, PII, or To-C concurrency | Everything in `standard`, plus full restrict guardrails |
| `long-running` | Multi-module or multi-cycle, or the user asked for subagents | `references/long-running.md` and the matching class above |

Do not load `vk-restrict` for copy, rename, pure frontend, or a tiny patch that does not change data flow, IO, or dependencies.

Do not load `../references/gstack-bridge.md` until local verification finished, the class is not `trivial`, and a bridge entry criterion matches.

## Language references

Paths are **relative to this skill directory** (`vk-work/`), not
`$HOME/.codex/skills/vk-work/`.

1. Read `references/README.md` when you need any extra file.
2. If `references/{language}/README.md` exists, load it. `{language}` is `swift`, `golang`, `python`, …
3. If that directory is missing, say fallback and use repository conventions plus language-native checks. Do not invent framework rules.
4. For Swift / iOS / macOS, load `references/swift/README.md`. Prefer `vk-ios-agents` when the user asked for multi-skill iOS orchestration.

When a language reference exists, follow it for that task.

## vk-request mapping (only if a DSL is present)

Treat the DSL as the execution contract. Do not restate the task loosely.

Keep: `PROJECT CONFIG`, `SYSTEM ARCHITECTURE`, `GLOBAL STATE`, `PHASE STRATEGY`, `TASK DAG`, `CONSTRAINT SYSTEM`, `VALIDATION SYSTEM`, `SUCCESS CRITERIA`.

Map: `In Scope` → edit scope; `Out of Scope` → do-not-touch; `TASK DAG` → order; `VALIDATION SYSTEM` → checks; `SUCCESS CRITERIA` → done; `Known Issues` → risks. Carry `ASSUMPTION:` / `TBD`. If the DSL conflicts with the repo, report and prefer the repo.

## vk-restrict (backend IO / data-flow / dependency only)

Load `../vk-restrict/SKILL.md` before locking a backend design. Load
`../vk-restrict/references/backend-scheme-guardrails.md` only for detailed
or To-C rules. Convert the three-axis gate into implementation constraints
and verification items. Stop and report unhandled risks the user has not
accepted.

## Skeleton (every class)

1. **Scope lock** — in and out of scope; git baseline (`status`, `diff`, `diff --cached`); isolate unrelated dirty files.
2. **Implement** — production code in the locked files; short cycles; no speculative refactors.
3. **Test and accept** — enter `testing` when required implementation is
   ready. Map tests to required criteria, execute repo-native checks, and
   record passes/failures/blocked checks and exact baseline. Only passing
   required tests permit acceptance. Record actual user/agreed acceptance;
   failures return through repair -> retest -> reacceptance.
4. **Synchronize and hand off** — update the canonical requirement and
   linked review before declaring completion; extra summaries only if
   warranted; `vk-submit` only when the user asked to commit.

Frontend: visual consistency and simple UI structure.
Backend: correctness (transactions, authz, compatibility) before throughput tricks.

Do not add frameworks or mix frontend/backend paradigms. Follow the repo.

## Records and resume

- Follow [document lifecycle](../shared/document-lifecycle.md) for feature
  changes, repairs, completion, and acceptance. Resolve the existing
  requirement/review first; update current content, affected feature items,
  criteria, status, revision, and history in place. Log adjustments from any
  source, including implementation decisions and acceptance feedback.
- Follow [delivery workflow](../shared/delivery-workflow.md) for every
  functional task, including test-only and acceptance-feedback requests.
  Keep its ledger in the existing requirement; attach it before development.
  Gate handoffs with `../vk-request/scripts/check_delivery_lifecycle.py`.
  Native project requirements stay canonical; use their equivalent checker
  only with explicit mapping to all required gates.
- For a functional change without a requirement file, create a concise
  requirement in `./vk/request/`; do not force a full DSL. Internal-only
  edits without functional change remain subject to selective records.
- Start authorized work with affected items `in_progress` after scope
  confirmation. Enter `testing` when implementation is ready. Once required
  criterion-linked checks pass, record actual behavior/evidence and mark them
  `completed_pending_acceptance`. Mark `accepted` only on explicit user
  acceptance or a previously agreed acceptance mechanism; record its scope,
  time, and result. Partial completion must remain visible in aggregate status.
- Then mark `completed` only after the acceptance gate and final requirement,
  review, issue, and remaining-work synchronization check. Keep pending or
  failed acceptance visible even if implementation was committed/pushed.
- Preserve previous acceptance on later changes; reopen only affected items
  and record delivery iterations explicitly. Update linked findings with
  repair details and verification, never treating code edits as proof of a fix.
- Required requirement/review synchronization is part of completion even
  for a small repair. If it fails, report code complete/documentation pending.
- Ordinary Q&A and trivial verified edits: no `./vk/work/` file.
- Material or long-running work: one checkpoint `./vk/work/checkpoint.md`,
  updated in place (task ID, canonical requirement/review paths, HEAD, done,
  verification, blockers, next step). Link to document ledgers instead of
  copying them. On resume, confirm branch, commit, and relevant dirty diff
  before reusing conclusions.
- Optional extra summaries use a stable English slug, e.g.
  `task-summary-<slug>.md`; update an existing summary for the same matter.
- `.gitignore` must include `vk/`. Unstage with `git restore --staged -- vk/`.
- Migrate legacy dirs with `../vk-submit/scripts/migrate_vk_record_dirs.py`.

## Output

- `trivial`: summary card, what changed, verification. Skip empty Auto-evolution.
- `standard` / `high-risk` / `long-running`: summary card, objective and scope, changes, verification, risks, next action / Auto-evolution.

Title the card `😁 + short task summary`.
