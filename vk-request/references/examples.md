# vk-request example library

## How to use

- Reuse compression, field mapping, and minimal-assumption patterns.
- Do not copy the sample business content.
- When the user gave little information, prefer Example 4.

## Example 1: Web product MVP

### Input

```text
Build a bug-feedback tool for indie developers.
v1 only needs email login, submit feedback, admin list, and status.
No payments, team collab, or analytics.
Ship a thin slice to learn.
```

### Output notes

- `PROJECT_GOAL` is one goal: close the bug-feedback loop, not "build a full SaaS".
- `IN_SCOPE_LIST`: login, submit, status, admin.
- `OUT_OF_SCOPE_LIST`: payments, team ACL, reports.
- `CURRENT_PHASE`: `Phase 1 - MVP Bootstrap`.
- Short `TASK_DAG`:

```text
Task 1 Auth skeleton -> Task 2 Feedback write path -> Task 3 Admin list/status -> Task 4 Minimal validation
```

- `ASSUMPTION:` email OTP or magic link as the smallest login.

## Example 2: Multi-agent delivery

### Input

```text
Split a support knowledge-base Q&A system into parallel agent work.
Need ingestion, retrieval, answering, evaluation.
Get a runnable slice first. No rerank or permission system yet.
```

### Output notes

- `PIPELINE_A` through `PIPELINE_N` can map to ingestion, retrieval, answering, evaluation.
- `Custom Agents` get the minimum roles, e.g. `Agent 7 - Ingestion`, `Agent 8 - Evaluation`.
- `PHASE_1_GOAL`: one-round Q&A path runs and can be validated.
- `HARD_CONSTRAINTS`: no blocking on the main path; index build decoupled from online retrieval.
- `DO_NOT_LIST`: no early rerank, complex ACL, or human-workflow admin.

## Example 3: Async backend service

### Input

```text
Build an async transcode service: upload audio, transcode off the request path, callback the result.
Main path must not block. mp3 and wav first.
```

### Output notes

- `NFRS`: `async only`, `no blocking IO in main path`.
- `PIPELINE_A`: `Upload -> Queue -> Transcode Worker -> Callback`.
- `Agent 6 - Frontend` can be `Not used in current phase`.
- Validation: input format, state machine, failure retry.
- `FALLBACK_STRATEGY`: local mock callback first, then a real callback URL.

## Example 4: Sparse input, smallest executable DSL

### Input

```text
Turn an AI voice-product idea into an execution prompt template.
```

### Output notes

- Do not invent product details.
- `PROJECT_NAME` can be `TBD - AI voice product`.
- `SUCCESS_CRITERIA` as user-action language, not invented KPIs.
- Uninferable fields such as `LATENCY_TARGET`, `PIPELINE_B`, `KNOWN_ISSUES`:

```text
ASSUMPTION: latency target not provided yet; keep as TBD until product constraints are defined.
```

- Short `TASK_DAG`:

```text
Task 1 Clarify core user flow -> Task 2 Define minimal pipeline -> Task 3 Establish validation contract
```

- Structure complete, business content restrained. Prefer `TBD` over fake detail.
