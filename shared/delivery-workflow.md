# Delivery workflow and verifiable gates

Use for functional requirements from confirmation through completion,
including test-only work, acceptance feedback, and repairs. `vk-work` owns
execution/testing/retesting and records acceptance only when authorized.
`vk-request` maintains scope/criteria; `vk-review` analyzes findings;
`vk-submit` handles authorized submission independently of product acceptance.
Do not create separate competing documents or a new skill for each phase.
Apply [verification policy](verification-policy.md): phase transitions are
recorded gates, not instructions to restart all reviews/tests. Reuse valid
evidence, target affected criteria, and expand only for an identified risk.

## One requirement, one traceable ledger

Keep a single current ledger in the canonical requirement, including native
project requirements, between `<!-- vk:lifecycle:start -->` and
`<!-- vk:lifecycle:end -->`, with one fenced `json` object. Start from
[the small example](../vk-request/references/delivery-ledger.example.json).
Adapt its real scope, dates, IDs, and evidence; example results are not
evidence for a real project. Keep a DSL ledger outside chapters 0 through
14, before document history. Keep native requirements in their own format.

The ledger is the authoritative current delivery/test/acceptance/issue
closure state. Prose describes behavior and decisions; review documents
own analysis and repair details and link the same issue IDs/ledger. Do not
maintain a second independent issue-status table. Link existing project test
tools and evidence rather than duplicating entire test reports. If a project
already has a machine-readable equivalent, use its checker with an explicit
field/gate mapping; do not silently skip missing checks.

- `task_id`, `iteration`, and `status` match the document metadata.
- `features`: stable IDs, title, required flag, scope revision, implementation
  state/evidence, and criteria with stable IDs, descriptions, required flags.
  Advance affected feature scope revisions when requirements/criteria change;
  retain withdrawn items as not required with a decision in history.
- `confirmation`: who confirmed, timestamp, evidence of approval (including
  the user's actual task instruction when sufficient), and `scope_versions`
  covering current feature revisions. Do not request another approval when
  existing authorization already confirms the scope.
- `tests`: append runs with stable case `id`, unique `run_id`, criterion IDs,
  `scope_versions` for referenced features, `required`, and result
  `not_run | pass | fail | blocked`. Executed/blocked runs also record `at`,
  `baseline`, and actual `evidence`. The latest run per case controls the
  current test result; old failed attempts remain available.
- `baseline`: commit plus relevant dirty-diff fingerprint, or another exact
  tested build identifier. Passing tests on a different baseline or scope
  revision are stale. Unaffected test evidence may be carried forward only
  with an explicit impact assessment/run record identifying the source
  evidence and why it applies; never claim it was rerun.
- `acceptance`: append attempts with unique ID, criterion IDs,
  `scope_versions`, result `pending | pass | fail | blocked`, and for decided
  attempts `at`, `by`, `baseline`, `evidence`, and `mechanism: user | agreed`.
  An agreed mechanism also records the prior `agreement`. Acceptance must
  follow passing tests on the reviewed scope/build. Latest applicable
  attempts control each criterion; partial acceptance is explicit.
- `issues`: stable IDs, affected criteria, source stage, blocking flag,
  current status, and append-only `history` events with status, timestamp,
  and evidence. Failed/blocked test and acceptance records link an
  `issue_id` covering their affected criteria. Requirement ambiguities and
  development/review problems enter the same issue loop before testing.
- `events`: append chronological stage changes with status, timestamp, and
  evidence/reason. History is not overwritten on a retry or rollback.

The helper validates record structure, references, declared results,
freshness, transitions, and evidence presence. It cannot independently
prove that tests ran or that a user approved; inspect referenced outputs
and actual authorization. A checker PASS is not business acceptance.

## Stages and exit conditions

| Status | Meaning / next gate |
| --- | --- |
| `awaiting_confirmation` | Draft goal/scope/features/criteria; resolve material ambiguity and record approval |
| `ready` | Current scope confirmed; begin authorized development |
| `in_progress` | Implement or repair; document actual changes and affected scope |
| `testing` | Required implementation complete with evidence; every required criterion has a required test case; record tested baseline |
| `completed_pending_acceptance` | All required latest tests pass on current scope/baseline; no unresolved blocking issues; ready for acceptance |
| `accepted` | Every required criterion accepted by user/agreed mechanism after tests; record partial/failed attempts separately |
| `completed` | Acceptance gate passes and final requirement/review synchronization and residual-work check recorded in `closure` |
| `blocked`, `deferred`, `cancelled` | Record reason and resumption/withdrawal decision; never count as passed |

Do not jump forward across stages on existing records. A task that starts
with existing completed work may import its actual evidence/history; do
not fabricate stage events or approvals. Use `accepted` for acceptance,
then `completed` for the final documentation/closure check; commit/push is
neither event. A task can be submitted while awaiting acceptance when the
user authorizes submission. Report its real delivery status.

Before `completed`, add `closure` with `at`, `by`, `evidence`, and
`documents_synced: true` only after checking the canonical requirement,
linked reviews, feature/test/acceptance coverage, issue dispositions, and
remaining work. Keep optional outstanding work explicitly out of the
required accepted scope; do not silently lower requirements to pass.

## Failure, repair, retest, reacceptance

1. In any stage, record the issue under the existing matter/iteration and
   link affected criteria and evidence. A new root cause gets a new ID;
   the same failure/regression reopens its existing ID.
2. Determine whether it is a defect against the agreed criterion or a
   requirement change. Defects return affected work to `in_progress`;
   material scope changes return to `awaiting_confirmation`, update current
   text/criteria and affected scope revisions, and record authorization.
3. Record repair/adjustment and update the same issue to
   `fixed_pending_verification`. Neither edited code nor a changed expected
   result proves resolution. Keep unresolved blocking issues visible.
4. Enter `testing` and append new runs. On verified resolution, record
   `resolution: {kind: repair | requirement_change, at, baseline, scope_versions, evidence}`
   and `retest_runs` naming exact passing run IDs after the repair, covering
   every affected criterion. Append the `verified_resolved` event after
   retesting. Historical successful retests remain valid historical evidence
   when later code changes; current delivery still needs fresh test results.
5. Re-enter acceptance after required retests pass. Affected criteria need
   acceptance after the issue handling; earlier acceptance remains in history.
   Unaffected feature acceptance is retained when its scope is unchanged.
   A failed or blocked acceptance cannot be replaced by developer judgment.
6. Repeated failure uses the same records within the finite repair limit;
   it does not mandate unlimited retries. Stop at the limit/no-progress
   condition and record the blocker/next decision. Reopen only affected
   criteria, retaining applicable evidence for unchanged features. `deferred`
   blocking issues prevent progression. `not_applicable` needs a documented
   reason/decision; removing scope requires the approved requirement change.

## Check and save

```bash
python3 <vank>/vk-request/scripts/check_delivery_lifecycle.py <canonical-requirement.md>
python3 <vank>/vk-request/scripts/check_delivery_lifecycle.py <canonical-requirement.md> --gate completed
```

The first command checks the current stage; the second checks readiness for
completion without changing it. Use `--gate testing`,
`--gate completed_pending_acceptance`, or `--gate accepted` for handoffs.

For local requirements under `vk/request/`, the save helper enforces these
gates before atomic replacement, retains document history, and checks
append-only attempts/events against the existing file. Pass current body
(without metadata/managed history), expected revision, and change reason:

```bash
python3 <vank>/vk-request/scripts/save_request_doc.py \
  --format requirement --path vk/request/REQ-001-purchase.md \
  --expected-revision 3 --status testing \
  --change-summary "Implementation ready; enter functional testing"
```

Default `--format dsl` additionally validates DSL chapters. The helper keeps
the ledger status synchronized with `--status`; append a matching workflow
event in the input. Early unconfirmed legacy drafts may remain ledger-free;
attach a ledger before advancing them. Existing ledger-free advanced records
must be adopted with truthful current evidence before the next update;
do not rewrite their original history or mark them accepted automatically.
