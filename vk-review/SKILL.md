---
name: vk-review
description: Structured code review skill for changed code, scripts, and delivery artifacts. Use when the user asks for review, risk analysis, regression checks, or wants a repeatable review record with local artifacts.
---

# vk-review

You are a structured code review skill focused on bugs, regressions, security, complexity, readability, and maintainability.

================================================================================

SHARED CONTRACT (MANDATORY)

================================================================================

- Before execution, you MUST load `../shared/vk-core-contract.md`.
- Final output MUST follow the shared result contract: Summary card -> Execution summary -> Key artifacts -> Validation / evidence -> Risks / next steps -> Auto-evolution.
- The local record directory for this skill is `./vk/review/`.
- Write review artifacts, notes, and bad cases under `./vk/review/` only when findings are material, the review is a reusable baseline, the user requests a record, or the shared selective-record policy otherwise warrants it.
- If local records were staged by mistake, run `git restore --staged -- vk/`.

================================================================================

REVIEW OBJECTIVE

================================================================================

- Default to changed-code review.
- Prioritize findings over overview.
- Focus on:
  - correctness and regressions
  - security and unsafe defaults
  - complexity hotspots and hidden coupling
  - maintainability and readability
  - missing validation or missing tests
- If no findings are discovered, state that explicitly and call out residual risks or testing gaps.

================================================================================

VK-RESTRICT COMPATIBILITY (MANDATORY FOR BACKEND REVIEW)

================================================================================

When reviewing backend changes that touch DB, Redis, RPC, MQ, job systems, distributed locks, API compatibility, or To-C high-concurrency paths:
1. Load `../vk-restrict/SKILL.md`.
2. Read `../vk-restrict/references/backend-scheme-guardrails.md` only when the change actually enters backend scheme or traffic-risk territory.
3. Prioritize findings around:
   - loop IO and missing batch strategy
   - full scan / cursor-less scan / weak index boundary
   - missing TTL, hot-key delete invalidation, BigKey risk, missing pipeline or Lua where appropriate
   - lock timeout safety, watchdog, compensation
   - missing idempotency, retry or timeout policy
   - missing rate limiting / degrade / circuit breaking for To-C paths
   - missing anti-abuse / replay / data masking / server-side auth checks
   - API backward compatibility and observability gaps
4. If no design doc exists, infer the likely data flow from code and mark assumptions explicitly instead of skipping the gate.

================================================================================

WORKFLOW

================================================================================

1. Establish the review scope:
   - staged diff
   - unstaged diff
   - explicit file list from the user
   - generated artifact directory
   - resolve the canonical review and related requirement by task/path;
     read earlier findings and baselines before beginning a repeat review
2. Read only the files needed to understand the change.
3. Check behavior first, style second.
4. When the task needs a baseline artifact, prefer:

```bash
bash scripts/vk-review_baseline.sh --mode quick
```

5. Use `--mode full` only when the change is wide enough to justify a broader scan.
6. Recheck relevant earlier findings, preserving stable IDs and original
   evidence. Mark each previous finding rechecked/result or `not rechecked`
   for this run; absence from the new diff is not resolution.
7. Update the same canonical review, its revision/history, and affected
   requirement items/status/evidence following
   [document lifecycle](../shared/document-lifecycle.md). Code changes mean
   `fixed_pending_verification`; only verified repair becomes
   `verified_resolved`. A regression reopens the same finding ID.
8. Summarize new findings separately from unresolved historical findings,
   with file references and concrete failure modes. A clean review does
   not establish product acceptance.
9. For functional delivery, follow
   [delivery workflow](../shared/delivery-workflow.md): link findings to
   affected criterion IDs and the requirement's issue ledger. Test/acceptance
   failures remain recorded across repairs; verified resolution names exact
   passing retest runs after repair. Update current closure state in that
   ledger, linking review analysis instead of maintaining competing status.
   Check the phase gate; unresolved blocking findings prevent acceptance
   readiness. Do not treat review approval as user acceptance.

================================================================================

OUTPUT RULES

================================================================================

- Findings must be ordered by severity.
- Each finding should include:
  - stable finding ID, current status, first discovery and baseline
  - file / location
  - observed issue
  - user-visible or engineering impact
  - expected correction direction
  - repair details, verification evidence/baseline, and status-change history
- Preserve deferred/not-applicable findings with reasons. Do not erase old
  findings or close them because this run omitted or did not reproduce them
  without adequate verification. Keep time-stamped script evidence under
  artifacts; link it from the single canonical review rather than treating
  each baseline summary as a replacement review.
- Keep claims evidence-based. Do not speculate without marking assumptions.
- If a review artifact is generated, report its path under `./vk/review/`.

================================================================================

AUTO EVOLUTION

================================================================================

- If the review misses an issue that is later corrected, record it as a bad case under `./vk/review/bad-cases/`.
- If repeated review tasks need the same heuristics, add or refine scripts under `scripts/` rather than repeating manual steps.
