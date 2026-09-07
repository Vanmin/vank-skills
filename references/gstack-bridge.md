# Vank–gstack Delivery Bridge

Use this reference only from `vk-work` after local build and the matching
verification-matrix checks. Vank remains the controller and the owner of
durable project records under `./vk/`. gstack supplies specialist execution
only where it has a real advantage.

Do not load this file for a trivial edit. Do not load it merely because
gstack is installed.

## Ownership

| Concern | Owner |
| --- | --- |
| Backend implementation, transactions, concurrency, API tests, language-native profiling | Vank (`vk-work`, `vk-restrict`, `vk-review`) |
| Browser / visual acceptance when a user-visible web page changed | gstack `browse` (or `qa` in inspect-only mode) |
| High-risk auth, payments, PII, secrets — at design time, not after the fact | `vk-restrict` first; gstack `cso` only if installed and the user wants that extra pass |
| Ordinary commit and push | `vk-submit` only |
| Explicitly authorized PR land or deploy | gstack `ship` / `land-and-deploy` **instead of** `vk-submit`, never both |
| Post-deploy observation after a user-authorized deploy | gstack `canary` |

Choose exactly one command owner for commit and push.

## Selection

Select a specialist only when its entry criteria match **and** the installed
skill actually covers that job.

| Entry criteria | Specialist | Do not use it for |
| --- | --- | --- |
| A user-visible web flow changed, or a browser regression is plausible | `browse`, or `qa` without its submit/fix-and-commit steps | Backend capacity, DB, MQ, API-only changes |
| User explicitly wants an independent security review of a high-risk change | `cso` | Substituting `vk-restrict` data-flow gates |
| User explicitly authorizes landing a PR or deploying | `ship` or `land-and-deploy` | Ordinary scoped commits |
| A deployment already happened and the user authorizes observation | `canary` | Inventing production access |

Do **not** map "latency / throughput / backend performance risk" to gstack
`benchmark`. That skill is web-page loading, Web Vitals, and asset weight. For
backend capacity use language-native tools (`go test -bench`, pprof, k6/HTTP
load against the service) and record the interpretation in `./vk/work/` only
when the run is material.

Do **not** let gstack `qa` commit, push, or "fix then submit". If `qa`
instructions include those steps, stop after inspection/evidence and return
control to Vank.

Do not run both `vk-review` and gstack `review` on the same diff by default.

Follow the selected gstack skill in full only inside the boundary above. If
its instructions conflict with the user's authorization, stop and report.

Do not hardcode paths to gstack, copy its scripts, or assume browser,
deployment, cookie, or production credentials exist.

## Evidence handoff

Before invoking a selected specialist, give it: change scope, target
environment, acceptance criteria, known risks, and any safe fixture the user
supplied.

After it returns, if a `./vk/work/` record already exists for this task,
append:

- selected specialist and why
- command or flow and outcome
- evidence location, or why evidence could not be captured
- remaining risk, owner, next action

If no bridge gate matched, say that Vank-only verification was deliberate.
Do not create a record just to document a skipped bridge.
