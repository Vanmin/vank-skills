# Backend Scheme Guardrails

## When to read this file

- Load only after the task is confirmed as backend design, architecture review, implementation gating, or backend review.
- This is the detailed rule book for `vk-restrict`. Do not paste it wholesale into host output. Distill constraints, gates, and verification items.

## 1. Three-axis frame

### Data flow

- Draw the shortest business chain: request entry -> validation -> auth -> read/write path -> async path -> callback/compensation.
- For each hop answer: where data comes from and goes, sync vs async, whether it stampedes origin, who compensates on failure, whether the user is blocked on the main path.

### IO

- Count IO on the main and async paths: MySQL, Redis, RPC/HTTP, MQ, cron/scan jobs.
- Goal: fewest IO to finish the job, with batching, degradation, and rate limits on hot paths.

### Dependencies

- List upstream entry, this service, hard deps, soft deps, degrade path.
- Ask whether a dependency failure becomes an avalanche or visible user jitter.

## 2. Database and IO rules

### 2.1 IO in loops

- Do not issue MySQL, Redis, or RPC IO inside a `for` loop.
- Prefer batch APIs: Redis `MGET` / `HMGET`, SQL `IN` / bulk write, batch RPC.
- If batching is impossible now, label it as a blocking risk and name the convergence path.

### 2.2 Scans

- Avoid wide table scans and full cache scans.
- Avoid unindexed queries and unbounded Redis scans.
- When a scan is required, require off-peak execution, cursor or limit, per-batch cap, and interrupt/resume.

### 2.3 Read/write strategy

- State read/write ratio before choosing indexes and storage.
- For hot synchronous writes, evaluate async write, bulk write, or MQ/Redis then batched persist.
- Do not push a burst of synchronous writes onto MySQL at peak.

## 3. Redis

### 3.1 TTL

- Keys need a sensible TTL by default.
- Long-lived keys are for rare config dictionaries only.
- TTL that is too short causes origin stampedes.

### 3.2 Hot keys and breakdown

- Do not invalidate a hot key with delete-then-lazy-load.
- Prefer active update, logical expiry, a mutex, or single-threaded origin refresh.

### 3.3 BigKey

- Estimate size before choosing a structure.
- Split by business or time dimension when needed.

### 3.4 Pipeline / Lua

- Independent commands: Pipeline.
- Atomicity: Lua.
- Do not split Redis calls that can share one RTT.

## 4. Distributed robustness

### 4.1 Locks

- Set a reliable lease.
- Answer: what happens if work outlives the lock; what happens after a pod restart.
- Common fallbacks: watchdog renew, compensation jobs, idempotent replay.

### 4.2 Idempotency

- MQ consumers, cron, and external callbacks that mutate state must tolerate duplicates.
- "It should only run once" is not a design.

### 4.3 Runtime and retry

- For cron and MQ: duration, concurrency, retry interval, max retries, DLQ/alert/human path.

## 5. To-C extras

### 5.1 Traffic protection

- Evaluate rate limit, degradation, and circuit break.
- Rate limit: QPS cap, gateway vs app, friendly overflow response.
- Degradation: which paths are non-core, what can turn off at peak.
- Breaker: which downstreams are risky, how to fail fast.

### 5.2 Cache and RT

- User-facing core APIs care about TP99, often 200ms or 100ms.
- Hot, slowly changing data: local cache -> Redis -> DB.
- Do not make the user wait for work that can be async.

### 5.3 Abuse and safety

- Asset, signup, and lottery paths need risk control or bot checks.
- Recover `userId` from the token server-side; do not trust client-supplied IDs.
- Replay protection: nonce, timestamp, signature.
- Mask phone, ID, and bank numbers in logs and UI.

### 5.4 Compatibility

- App/mini-program clients stay on old versions.
- Published APIs stay forward compatible: no silent field deletes, no semantic flips, new required fields need defaults, version `/v1` `/v2` when needed.

### 5.5 Observability

- TraceId on the main chain.
- Metrics: error rate, RT, core business KPIs, queue depth.
- Support reconstructing the full chain from a user identifier during complaints.

## 6. Where to land output

### `vk-request`

- `NFRS`, `Data Flow Rules`, `Constraint System`, `Validation System`, `Success Criteria`

### `vk-work`

- controller ledger, implementation constraints, verification checklist, residual risks

### `vk-review`

- high-priority findings, missing gates, behavior regression risk, missing tests/monitoring/compat policy
