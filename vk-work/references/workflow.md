# vk-work detailed workflow

Load for `standard` or `high-risk` work. Trivial edits use the four-step
skeleton in `SKILL.md` only.

Follow internally in order. Do not dump this file into the user reply.

## 0. Task design

Restate the task. Split into executable sub-tasks. Name in-scope and
out-of-scope. Classify `trivial` | `standard` | `high-risk` | `long-running`.
For functional work, resolve the canonical requirement and ledger. Confirm
scope/criteria against existing user authorization before entering development;
read `../../shared/delivery-workflow.md`. Do not ask for redundant approval.

## 1. Responsibility

Name modules allowed to change. Do not expand past the request.
Classify repair authority: safe auto-repair / repair after evidence / never
without the user.

## 2. Git baseline and scope lock

Capture before edits:

- `git status --short --branch`
- `git diff --name-only`
- `git diff --cached --name-only`

Isolate unrelated dirty files. Refresh the baseline after a major repair
cycle on long-running work.

## 3. Structure

Find the files to change. Confirm frontend vs backend. For Swift, also
identify lifecycle, state ownership, async, and persistence/security
boundaries (then load `swift/README.md`).

## 4. Design

Minimal solution. Simple > clever. Local impact > global refactor.
Do not trade away security or an explicit performance SLO.

## 5. Implement in short cycles

Production code only. After each slice: compile/typecheck → targeted
tests → one control decision → safe auto-repair if the failure is
reproducible and in scope → re-check.

Control decision is exactly one of: continue, repair, broaden
verification, redesign, escalate.

Apply `../../shared/verification-policy.md`: stop when the same failure
repeats without narrowing; default to at most two automatic repairs per
same issue/root cause across skills/sessions. Preserve attempts/evidence
and report the blocker/next decision at the limit.

## 6. Readability

Comment non-obvious invariants only. Follow the project's formatter/linter
when present. Missing Vank helper scripts must not block completion.

## 7. Verification

Enter `testing` only when required implementation is complete and each
required criterion has a test case. Record the tested commit/dirty baseline.
Choose reuse/targeted/broader from changed scope, risk, and earlier evidence.
Run only necessary repo-native tests/lint/build for the slice. Then apply
`verification-matrix.md` rows that match the diff.

Distinguish compile evidence, targeted tests, broadened regression, and
blocked checks. Failed required checks mean the task is not complete.
Append individual test attempts/results to the canonical requirement ledger;
do not replace earlier failures. Run the lifecycle acceptance-readiness gate.
For any failure, record/link the same issue, repair or confirm a scope change,
then retest before accepting the affected criteria. Explicitly track untested,
failed, and blocked items; compiler/lint success alone is not functional proof.
Passing sufficient checks ends verification for that scope. A new full
review/suite requires changed behavior, a new failure/risk, explicit scope,
or a project-required check; a phase transition alone is insufficient.

## 7.1 Acceptance and closure

When all required tests pass and blocking issues are resolved, enter
`completed_pending_acceptance`. Check every required criterion against actual
user acceptance or the agreed mechanism. Record partial/failing/blocked
attempts; failures return to development/confirmation, then testing and
reacceptance. Mark `accepted` only when all required criteria passed.
Run the `completed` gate after final requirement/review synchronization and
residual-work checks, record closure, then mark `completed`. A code-complete
handoff awaiting the user is reported as pending acceptance, not full closure.

## 8. Synchronize documents and apply git hygiene

Before completion, follow `../../shared/document-lifecycle.md`: update the
canonical requirement's current behavior, feature items, criteria, states,
revision/history, and evidence; update linked review repair/recheck states.
Create a concise requirement if a functional change has none. This is
mandatory even when no additional execution record is warranted. Required
checks passing means completed pending acceptance, not automatically
accepted. On acceptance, record the user/agreed mechanism, scope, time,
and result. Preserve earlier acceptance and iteration history.

Selective records only. One checkpoint file for a long task, updated in
place: `./vk/work/checkpoint.md`.

English slug unless the user asked otherwise, for example
`task-summary-<slug>.md`.

Migrate with the script next to `vk-submit` inside the vank bundle:

```bash
python3 ../vk-submit/scripts/migrate_vk_record_dirs.py --repo-root .
```

Ensure `.gitignore` has `vk/`. Unstage records with `git restore --staged -- vk/`.
Compare the post-change diff to the Step 2 baseline.

## 9. Submit handoff

If the user asked to commit, hand off to `vk-submit` with objective, file
scope, verification evidence, risks, and canonical requirement/review
paths/revisions/status. Do not ad-hoc commit.
