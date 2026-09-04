---
name: vk-request
description: Compress natural-language intent into a structured prompt DSL aligned with MULTI-AGENT CODING ORCHESTRATION TEMPLATE V3-FINAL. Use when the user wants a prompt, DSL, system prompt, multi-agent template, or execution-controller template. Return inline unless the user asks to persist it under ./vk/request/.
---

# vk-request

## Shared Contract

- Load `../shared/vk-core-contract.md` before acting.
- Follow the shared result contract: start with a summary card, then structured body and Auto-evolution.
- Local records go under `./vk/request/`.
- The requested DSL is the direct deliverable. Add a separate result summary or Auto-evolution note only when the shared selective-record policy warrants it.

## vk-restrict compatibility (required for backend schemes)

- Load `../vk-restrict/SKILL.md` when the request involves backend design, APIs, DB, Redis, RPC, MQ, cron, distributed locks, or To-C high-concurrency paths.
- Progressive disclosure: read the restrict skill first; load [../vk-restrict/references/backend-scheme-guardrails.md](../vk-restrict/references/backend-scheme-guardrails.md) only for detailed backend or To-C rules.
- Embed restrict output in existing template fields only. Prefer `NFRS`, `Data Flow Rules`, `Known Issues`, `Constraint System`, `Validation System`, `Success Criteria`, `DO_NOT_LIST`.
- Backend DSLs must encode: main data-flow chain, no IO-in-loop, batch read/write, scan boundaries, cache TTL / hot-key policy, idempotency, retry/timeout, compatibility, observability. To-C adds rate limit / degrade / break, abuse prevention, and RT.
- Missing facts become `ASSUMPTION:` / `TBD`. Do not invent capacity, QPS, RT, or storage choices.

## Purpose

- Compress the user's goal into an executable prompt DSL, not a loose design essay.
- Reuse the template skeleton and keep chapters `0` through `14`.
- Make only the minimum assumptions required. Do not widen scope.
- Write the requested DSL to `./vk/request/` only when the user asked for a durable file; otherwise return it inline.

## What this skill is

- Value is structure and constraints, not a pretty prompt.
- A DSL that names goal, scope, phases, task DAG, validation, and failure handling pushes models toward plan -> act -> verify -> update state.
- Accurate claims: this DSL raises the chance of planner/controller/verify behavior. It does not impersonate host internals, unlock hidden modes, or depend on magic tokens.

## Hard rules

- Extract goal, success criteria, scope, constraints, architecture, phases, task DAG, and validation first.
- Keep English chapter names, control statements, and structure from the template.
- Required-but-missing fields use `TBD` or `ASSUMPTION:`. Do not fabricate.
- Even when multi-agent orchestration is a poor fit, emit the same DSL and minimize unused agents/pipelines.
- Do not emit generic advice. Emit a savable DSL.
- Do not leave `<<PLACEHOLDER>>` in the final result.
- Use one missing-field policy per field class. Do not mix blanks, guesses, `TBD`, and `ASSUMPTION:` for the same class.
- Default to the smallest executable DSL. Do not start with a questioning round.

## Procedure

1. Read the raw request and extract: `PROJECT_NAME`, `PROJECT_GOAL`, `SUCCESS_CRITERIA`, `IN_SCOPE_LIST`, `OUT_OF_SCOPE_LIST`, `NFRS`, `PIPELINES`, `TASK_DAG`, `KNOWN_ISSUES`.
2. Open [references/prompt-dsl-template.md](references/prompt-dsl-template.md) and fill chapters in order.
3. Minimal closure for missing fields: only what the template needs to run. One-sentence assumptions.
4. Missing-field policy:
- Direct `TBD`, no guesses: `PROJECT_NAME`, `PROJECT_GOAL`, `SUCCESS_CRITERIA`, `IN_SCOPE_LIST`, `OUT_OF_SCOPE_LIST`, `PHASE_2_NAME`, `PHASE_2_GOAL`, `PHASE_2_OUTPUT`, `PHASE_N_NAME`, `CUSTOM_AGENTS`.
- Required defaults (never blank, never `TBD`): `CURRENT_PHASE` = `Phase 1 - Bootstrap`; `DONE_TASKS` = `None`; `PENDING_TASKS` = `Task 1 - Define minimal executable slice`; `ACTIVE_PIPELINES` = `Pipeline A only`; `SYSTEM_STATUS` = `Planning`; `PHASE_1_NAME` = `Bootstrap`; `PHASE_1_GOAL` = `Define the smallest executable implementation slice`; `PHASE_1_OUTPUT` = `Minimal executable scaffold`; `PHASE_1_EXIT` = `First end-to-end path is executable and validated`; `TASK_DAG` = `Task 1 -> Task 2 -> Task 3`; `HARD_CONSTRAINTS` = `No out-of-scope features`; `SOFT_CONSTRAINTS` = `Readability preferred`; `DO_NOT_LIST` = `Do not add features not explicitly requested`.
- Must be `ASSUMPTION:` or `TBD` (execution boundary): `LATENCY_TARGET`, `NFRS`, `PIPELINE_A`, `PIPELINE_B`, `PIPELINE_N`, `DATA_FLOW_RULES`, `KNOWN_ISSUES`, `API_SPEC`, `DEPENDENCIES`, `FALLBACK_STRATEGY`, `USER_ACTION_1`, `USER_ACTION_2`, `USER_ACTION_3`.
- `CURRENT_PHASE`, `ACTIVE_PIPELINES`, `SYSTEM_STATUS`, `TASK_DAG` must stay executable. Do not write "plan later" filler.
5. Clarification cap:
- Ask only if the gap changes `PROJECT_GOAL`, `SUCCESS_CRITERIA`, `IN_SCOPE_LIST`, `OUT_OF_SCOPE_LIST`, `NFRS`, the main architecture, or whether multi-agent is required.
- Do not ask about fields that `TBD`, defaults, or `ASSUMPTION:` can hold.
- At most 3 questions, each able to change DSL structure.
- If the user does not reply, continue with this skill's missing-field policy.
- Prefer questions on scope, success criteria, core NFRs, and whether this is truly multi-agent.
- Defer `PHASE_2_*`, `PHASE_N_NAME`, non-critical Custom Agents, and defaultable status fields.
6. Reuse compression patterns from [references/examples.md](references/examples.md).
7. Reply order: Summary card, Request summary, Key assumptions, Prompt DSL, Document path, Validation, Auto-evolution.
8. Save immediately:

```bash
python3 vk-request/scripts/save_request_doc.py \
  --title "<title>" \
  --source-request "<raw user request>"
```

Pipe the full result on stdin.
9. Validate immediately:

```bash
python3 vk-request/scripts/validate_request_doc.py "<document-path>"
```

Only a passing validation is a final answer. On failure, fix, save, and validate again.

## Output format

- Spoken language follows the user.
- Lead with a summary card titled `😁 + short task summary`.
- Put the Prompt DSL in a fenced block.
- Document path must be the path the save script returned.
- Validation must quote the checker result.
- If a script fails, report the error. Do not pretend the file was written.
- If the run exposed a template pitfall, information-gap pattern, or external-practice shift, add Auto-evolution and `::automation-update{...}` when useful.

## Compact mode

- Enter compact mode when the request has fewer than 3 concrete features, or is clearly "organize thoughts / emit a template / bootstrap".
- Keep `Pipeline A` only; others `Not used in current phase`.
- Expand `Agent 0` plus 1-2 agents on the current task; unused agents `Not used in current phase`.
- Non-multi-agent work may set `Custom Agents` to `None`.
- Expand `Phase 1` only; `Phase 2` and `Phase N` may be `TBD`.
- `TASK_DAG` is a 2-4 node executable spine. No fake task padding.
- Structure complete, content restrained. Do not pad empty chapters.

## Persistence (when a durable file is requested)

- Directory: `./vk/request/`
- Filename: `request-YYYYMMDD-HHMMSS-<slug>.md`
- `slug` from title, else `untitled`
- Frontmatter must include `title`, `created_at`, `source_request`, `template_version`
- Save the structured result itself. Do not write a second summary.

## Git hygiene (when a durable file was created)

- Migrate legacy record dirs first:

```bash
VK_SKILLS_DIR="${VK_SKILLS_DIR:-$HOME/.codex/skills}"
python3 "$VK_SKILLS_DIR/vank/vk-submit/scripts/migrate_vk_record_dirs.py" --repo-root .
```

- `./vk/request/` stays local and untracked.
- Ensure `.gitignore` has `vk/`; add `vk-*/` only when the repository is not
  the Vank package source, where that pattern would ignore tracked child skills.
- If staged by mistake: `git restore --staged -- vk/ 'vk-*'`

## Template boundary

- Template: [references/prompt-dsl-template.md](references/prompt-dsl-template.md)
- Examples: [references/examples.md](references/examples.md)
- Do not rewrite `PLAN → ACT → VERIFY → UPDATE STATE → LOOP`.
- Do not add methodology chapters the template does not have unless the user asked to extend it.
