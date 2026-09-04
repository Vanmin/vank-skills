---
name: vk-restrict
description: Gate backend design and review across data flow, IO, and component dependencies. Covers DB/Redis/RPC/MQ/cron/locks, To-C concurrency, abuse prevention, compatibility, and observability. Use for scheme design, technical review, risk gates, or as a progressive constraint layer for vk-request, vk-work, and vk-review.
---

# vk-restrict

## Shared Contract

- Load `../shared/vk-core-contract.md` before acting.
- Follow the shared result contract: start with a summary card, then structured body and Auto-evolution.
- Local records go under `./vk/restrict/`.
- Write reusable constraint lists, risk gates, bad cases, or review baselines to `./vk/restrict/`.
- If records were staged by mistake: `git restore --staged -- vk/ 'vk-*'`.

## Purpose

- Compress "what a backend design must respect" into executable, reviewable constraints.
- Always reason on three axes: data flow, IO, component dependencies.
- Prefer defects that cause latency, instability, compatibility breaks, or incident amplification.
- Default hosts: `vk-request`, `vk-work`, `vk-review`. Also valid when invoked alone.

## When to load

- Only for backend or backend-adjacent infrastructure. Do not attach this to pure frontend, copy, or local rename work.
- Enable when any of these appear:
  - scheme / architecture / technical review
  - database, cache, RPC, MQ, cron, distributed lock
  - To-C traffic, high concurrency, low RT, risk control, abuse prevention
  - read/write path, async path, consistency, retry, idempotency, degradation, circuit break
- For a tiny patch that does not change data flow, IO, or dependency boundaries, degrade to a short checklist.

## Progressive disclosure

- Read this file first and decide whether the task is actually a backend-constraint problem.
- Load [references/backend-scheme-guardrails.md](references/backend-scheme-guardrails.md) only when detailed rules are needed.
- Do not restating the host skill's execution loop. This skill is a constraint and gate layer.

## Three-axis frame (required)

### 1. Data flow

- Main chain: entry -> validate -> read path -> write path -> async path -> compensation.
- Mark sync/async boundaries and who owns failure.
- Look for cache stampede, write fan-out, dual-write drift, missing compensation, and user-blocking work that could be async.

### 2. IO

- List DB / Redis / RPC / MQ / cron IO on the main chain.
- Check: IO in loops, batching, unbounded scans, index/cursor/limit/batch caps, sync vs async vs bulk writes, retry/timeout/idempotency closure.

### 3. Dependencies

- List callers, this service, downstreams, and side paths.
- For each: duty, RT, failure mode, degradation.
- Look for long chains, failure amplification, missing breaker/limit/degrade, client compatibility risk, missing traces and core alerts.

## Host mapping

### `vk-request`

- Do not add template chapters. Embed constraints in existing fields.
- Prefer: `NFRS`, `Data Flow Rules`, `Known Issues`, `Constraint System`, `Validation System`, `Success Criteria`, `DO_NOT_LIST`.
- If information is missing, write `ASSUMPTION:` / `TBD`. Do not invent QPS, RT, capacity, indexes, or storage choices.

### `vk-work`

- Finish the three-axis gate before locking the design.
- Put constraints into the controller ledger and verification list, not as verbal reminders.
- If a design violates a gate and the user has not accepted the risk, report before implementing.

### `vk-review`

- Use this skill as the backend risk dictionary.
- Prefer findings that cause incidents, cache breakdown, compatibility breaks, dirty writes, or unrecoverable failure.
- If the code has no written design, you may infer data flow from code and must label assumptions.

## Minimum output

- Applicability
- Three-axis constraint summary
- Main gates / risks
- Host landing fields
- TBD

## Hard rules

- Empty advice such as "make it faster" is not output.
- Do not invent new middleware or subsystems outside the current architecture.
- Do not widen scope in the name of constraints.
- Do not skip To-C compatibility, abuse prevention, observability, or degradation.
