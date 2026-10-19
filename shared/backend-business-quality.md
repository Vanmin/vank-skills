# Backend Business-Layer Quality Contract

Use this contract when a backend application change adds or modifies handler,
service/usecase, domain, repository, or transport error behavior. It is an
implementation gate, not a post-hoc style review.

Do not apply it to simple scripts, one-off utilities, build/release scripts, test
fixtures, pure configuration, or migrations that do not implement business-layer
behavior. Apply it to production workers, cron jobs, and message consumers when
they own or change domain behavior.

## Ownership

- `vk-work` owns when this contract runs and blocks the next implementation slice.
- `vk-backend-quality` owns the reusable rules and can be invoked directly.
- `vk-restrict` owns data flow, IO, concurrency, abuse prevention, and dependency risk.
- `vk-review` rechecks the same rules on the final diff.

Do not duplicate the `vk-restrict` three-axis gate here.

## Required implementation loop

### 1. Repository baseline

Before editing, identify the repository's existing layer names, feature directory
shape, error type, response envelope, and test conventions. Preserve the local
pattern unless the task explicitly changes it. Do not invent a universal path such
as `internal/service` when the repository uses another layout.

### 2. Business contract before each slice

For every endpoint or use case, record enough information to implement and test it:

```text
Use case
Input and authorization checks
Preconditions
State transition or invariant
Domain error codes
Transport status/code/message mapping
Transaction and side effects
Idempotency / retry behavior when applicable
```

Missing facts become `TBD` or `ASSUMPTION:`. Do not silently choose business
semantics.

### 3. Per-slice gate

After one small implementation slice, run the checks below before starting the next
slice. A blocking finding stops the handoff to the next slice and to testing.

## Layer contract

The names vary by repository, but the dependency direction remains:

```text
handler / transport -> service / usecase -> domain + repository interface
repository implementation -> database / ORM / RPC client
transport error mapper -> domain error
```

Blocking violations:

- **BL-001**: handler imports SQL, ORM, or repository implementation details;
- **BL-002**: handler contains business state transitions or transaction orchestration;
- **BL-003**: service writes HTTP/RPC status, JSON, or transport response envelopes;
- **BL-004**: repository imports transport packages or owns user-facing messages;
- **BL-005**: raw SQL or driver errors can reach a transport response;
- **BL-006**: the same error-to-response mapping is reimplemented in multiple handlers.

## Error boundary

Use a two-step translation:

```text
database / driver error
  -> repository classification (not found, conflict, unavailable, internal)
  -> service/domain error with stable business code and safe message
  -> centralized transport mapping
```

Preserve the original cause for logs and tracing. Never return `err.Error()` to the
client. Unexpected errors map to a safe internal error while retaining the cause
for observability.

Use **BL-007** for raw error exposure or missing cause-to-domain translation.

## Types, literals, and reuse

- Use a named type with constants for finite business states, event kinds, roles,
  error codes, and other protocol values.
- Keep one registry for transport status, stable code, and safe message.
- Do not turn every local string into a constant. A literal becomes a gate issue
  when it represents a shared protocol value, state, or duplicated business rule.
- Search for an existing semantic helper before adding one. Extract only stable
  repeated behavior; do not create a generic `utils` layer for one call site.
- Keep functions focused on one business responsibility. Avoid arbitrary line
  limits; report concrete mixed responsibilities or duplicated branches.

Use **BL-008** for an untyped finite state or shared protocol value, and **BL-009**
for a duplicated or missing central error/response mapping.

## Structure and tests

- New files follow the repository's established feature shape and naming.
- A service test covers each meaningful business branch and domain error mapping.
- A handler/contract test covers transport status, code, and safe message.
- A repository test covers database error classification when that behavior changes.
- A change that adds a state transition documents the allowed transition and rejects
  invalid transitions.

Use **BL-010** for a file-shape violation and **BL-011** for missing branch or
transport contract coverage.

Use **BL-012** for duplicated semantic logic when an existing helper or domain
operation should be reused. Keep this finding tied to a concrete duplicate and
correction direction; do not report generic style preferences.

## Severity

- **Blocking:** layer violation, raw database error exposure, unstable or missing
  error mapping, invalid state typing, or missing required business boundary.
- **Repair before acceptance:** duplicated semantic logic, inconsistent feature
  structure, unclear function responsibility, or missing branch/contract tests.
- **Advisory:** naming, comments, or optional simplification with no concrete risk.

Do not block a change for personal style preferences or for abstractions that do not
improve a real boundary.

## Gate output

For each finding report:

- stable rule ID and severity;
- file and line or symbol;
- observed behavior and business/engineering impact;
- smallest correction direction;
- verification result after repair.

Run the gate against the changed feature scope. Broaden only when a concrete shared
boundary or regression requires it.
