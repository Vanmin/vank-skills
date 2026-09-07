# Backend Scheme Guardrails

## When to read this file

- Load only after the task is confirmed as backend design, architecture review, implementation gating, or backend review.
- Distill constraints, gates, and verification items. Do not paste this file wholesale.
- Every hard-looking rule below is a **default**, not a universal ban. Record: Applies / Risk / Allowed exception / Evidence.

## How to apply a rule

For each candidate constraint, write four fields before treating it as blocking:

| Field | Meaning |
| --- | --- |
| Applies | Which path, data, or SLO makes the rule relevant |
| Risk | What fails if the rule is ignored |
| Allowed exception | When the rule does not apply, and what must still be true |
| Evidence | How the exception or the compliant design will be verified |

Empty advice such as "make it faster" or "add a cache" is not a gate.

## 1. Three-axis frame

### Data flow

- Draw the shortest business chain: request entry -> validation -> auth -> read/write path -> async path -> callback/compensation.
- For each hop: where data comes from and goes, sync vs async, stampede risk, who compensates on failure, whether the user is blocked on the main path.

### IO

- Count IO on the main and async paths: MySQL, Redis, RPC/HTTP, MQ, cron/scan jobs.
- Goal: enough IO to preserve correctness first, then fewest extra round trips on hot paths.

### Dependencies

- List upstream entry, this service, hard deps, soft deps, degrade path.
- Ask whether a dependency failure becomes an avalanche or visible user jitter.

## 2. Database and IO

### 2.1 IO in loops

- **Applies:** N+1 chatty loops on a request path or hot job, where a batch API exists.
- **Risk:** latency cliffs, pool exhaustion, amplified downstream load.
- **Allowed exception:** cursor/page loops that *must* bound each batch (pagination, backfill, fan-out with a cap). One IO per page is expected; unbounded per-item IO is not.
- **Evidence:** show batch API or per-page cap, plus a test or EXPLAIN for the hot query.

### 2.2 Scans

- **Applies:** list/search/export/cron that can touch unbounded rows or keys.
- **Risk:** full table or `SCAN` without cursor blows up CPU and cache.
- **Allowed exception:** off-peak backfill with cursor or keyset, per-batch limit, and interrupt/resume.
- **Evidence:** index or keyset predicate, batch size, resume token.

### 2.3 Sync vs async writes

- **Applies:** a write whose durability, ordering, or user-visible ack matters.
- **Risk:** dropping a durable write onto MQ "for throughput" loses money, inventory, or audit; bursting sync writes at peak saturates primary.
- **Allowed exception:** derived or eventually-consistent projections may be async if the source of truth is already committed and compensation exists.
- **Evidence:** state what is durable at ack time; name the consumer retry/idempotency path.

## 3. Correctness first

### 3.1 Transactions, isolation, uniqueness, lost updates

- **Applies:** multi-row or multi-store mutations, counters, balances, unique business keys.
- **Risk:** partial commit, dirty/non-repeatable reads, duplicate unique keys, lost updates.
- **Allowed exception:** read-only or single-row compare-and-set with an explicit version/etag.
- **Evidence:** transaction boundary, isolation choice, unique constraint or idempotency table, concurrent-update test.

### 3.2 Database and messages

- **Applies:** dual-write to DB and MQ, outbox, callbacks.
- **Risk:** committed DB without event, event without DB, duplicate or out-of-order consumption.
- **Allowed exception:** at-least-once plus idempotent consumers; outbox/inbox if the product already has that pattern.
- **Evidence:** duplicate and out-of-order consumer tests; failure-replay path.

### 3.3 Tenants, object ACL, idempotency keys

- **Applies:** any To-C or multi-tenant mutate/read by id.
- **Risk:** cross-tenant or cross-object access; replayed clients double-charge.
- **Allowed exception:** none for authz on object ids; idempotency key scope (user, tenant, operation) and TTL must be explicit.
- **Evidence:** unauthorized and cross-tenant tests; key uniqueness window.

### 3.4 Timeouts, retries, pools, backpressure

- **Applies:** outbound RPC/DB/MQ on the request path or workers.
- **Risk:** retry storms, unbounded concurrency, pool wait, hung clients.
- **Allowed exception:** retries only with budget, jitter, and idempotent ops; bounded worker concurrency.
- **Evidence:** timeout and max-attempt numbers; pool size vs concurrency; what happens on cancel.

### 3.5 Schema change, backfill, compatibility, recovery

- **Applies:** migrations, dual-write periods, API field changes.
- **Risk:** lock storms, unreadable old rows, new code vs old rows, no rollback.
- **Allowed exception:** expand/migrate/contract with dual-read when needed; batch backfill with resume.
- **Evidence:** migration plan, backfill batching, old-and-new reader test, failure recovery.

## 4. Redis

### 4.1 TTL

- **Applies:** cache and ephemeral keys.
- **Risk:** no TTL grows memory; too-short TTL stampedes origin.
- **Allowed exception:** true source-of-truth keys (lock records, idempotency rows) with a documented eviction or TTL that matches the business window.
- **Evidence:** TTL or documented lifetime per key class.

### 4.2 Hot keys and breakdown

- **Applies:** hot read keys, delete-then-reload invalidation.
- **Risk:** thundering herd.
- **Allowed exception:** active update, logical expiry, single-flight refresh.
- **Evidence:** invalidation method named on the write path.

### 4.3 BigKey and Pipeline / Lua

- **Applies:** large collections or multi-command atomicity.
- **Risk:** slow commands, blocking Redis, split RTT, lost atomicity.
- **Allowed exception:** split by business/time; Pipeline for independent commands; Lua only when atomicity is required.
- **Evidence:** size estimate or command grouping.

## 5. Distributed robustness

### 5.1 Locks

- **Applies:** mutex around a critical section.
- **Risk:** lock timeout while work continues; lock lost on restart.
- **Allowed exception:** lease + watchdog or lock-free compare-and-set when that is the repo pattern.
- **Evidence:** lease, owner, timeout, compensation.

### 5.2 Idempotency and retry runtime

- **Applies:** MQ consumers, cron, external callbacks that mutate.
- **Risk:** duplicate side effects.
- **Allowed exception:** none for "it should only run once" as a hope; duplicates must be safe.
- **Evidence:** duration, concurrency, retry interval, max retries, DLQ/alert path.

## 6. To-C extras

### 6.1 Traffic protection

- **Applies:** public or bursty user-facing paths.
- **Risk:** overload, unfriendly errors.
- **Allowed exception:** internal admin tools with auth may skip public rate limits.
- **Evidence:** rate limit / degrade / breaker placement.

### 6.2 Cache and RT

- **Applies:** user-facing core APIs with an RT SLO.
- **Risk:** user waits on work that can be async; missing SLO.
- **Allowed exception:** do not invent TP99 numbers; use `ASSUMPTION:` / `TBD` or the repo SLO.
- **Evidence:** measured or documented SLO; what stays on the sync path.

### 6.3 Abuse and safety

- **Applies:** assets, signup, lottery, identifiers from the client.
- **Risk:** bots, IDOR, replay, PII in logs.
- **Allowed exception:** none for trusting client-supplied `userId`.
- **Evidence:** server-side identity, replay protection, masking.

### 6.4 Compatibility

- **Applies:** published HTTP APIs and app/mini-program clients.
- **Risk:** silent field deletes, new required fields, semantic flips.
- **Allowed exception:** versioned `/v2` when breaking is explicit.
- **Evidence:** compatibility note in the review or DSL.

### 6.5 Observability

- **Applies:** production user-facing or money paths.
- **Risk:** cannot reconstruct a complaint.
- **Allowed exception:** local prototypes.
- **Evidence:** TraceId, error/RT/KPI metrics, queue depth where relevant.

## 7. Where to land output

### `vk-request`

- `NFRS`, `Data Flow Rules`, `Constraint System`, `Validation System`, `Success Criteria`

### `vk-work`

- controller ledger, implementation constraints, verification checklist, residual risks

### `vk-review`

- high-priority findings, missing gates, behavior regression risk, missing tests/monitoring/compat policy
