# Verification matrix

Load this file from `vk-work` when the change is `standard` or `high-risk` and
touches backend behavior. Do not run every check on every task.

Pick rows that match the diff. Language-native tools come from the repo
(`go test`, `pytest`, linters). A passing schema or lint check is not
evidence for the rows below.

For every functional task, also apply `../../shared/delivery-workflow.md`:
map required criteria to test cases, append individual runs/results with
baseline/scope versions, and record failed/blocked checks as linked issues.
These risk-specific rows supplement criterion coverage; they do not replace
the required test -> acceptance -> closure gates.

| Change type | Evidence to collect |
| --- | --- |
| Database transaction | Rollback on failure; unique constraint conflict; concurrent update (lost update or version) |
| MQ / callback | Duplicate delivery; out-of-order; failed replay / DLQ |
| Authn / authz API | Unauthenticated access; cross-tenant; cross-object |
| Schema / migration | Migrate; backfill batch; old binary + new rows or new binary + old rows; recovery |
| High-concurrency path | Representative load: latency, throughput, pool/CPU/memory — not a web-vitals benchmark |

## Language tools (optional extras, not substitutes)

- Go concurrency: `go test -race` only finds races on executed paths. It does not replace business concurrency tests. See https://go.dev/doc/articles/race_detector
- Go/CPU: `go test -bench` or pprof when the hot path changed
- Other languages: use the project's test and race/data-race tooling when present

If a required check cannot run, say blocked and the impact. Do not claim the
row passed.
