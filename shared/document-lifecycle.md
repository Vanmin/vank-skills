# Durable document lifecycle

Read before writing a durable skill document or updating a requirement,
feature status, review finding, or acceptance result. Keep the existing
project documentation format when one exists; the fields below describe
information to preserve, not a reason to replace that format.

## Identity and resolution

- Give a matter a stable ID, for example `REQ-001`. Link requirement,
  review, and work records by that ID and their canonical paths.
- Before writing, prefer the user's path/ID, then the active task links or
  checkpoint, then existing documents. Match goal, scope, acceptance
  criteria, and relationships; a similar title or overlapping filename is
  insufficient. If multiple candidates remain plausible, ask which one
  applies before overwriting or creating a competing document.
- Keep one canonical file per matter and purpose. Preserve its path when
  the title changes. New matters receive new IDs; unrelated reviews may
  have their own review ID without inventing a requirement relationship.
- New local requirement/review filenames may be `REQ-001-<slug>.md` in
  `vk/request/` and `vk/review/`. Other document types use a stable scope
  slug. Reuse existing paths, including legacy timestamped paths.
- An existing designated product requirement file remains authoritative.
  Update it rather than creating a parallel DSL or a second source of
  status. Local work checkpoints link to it instead of copying its ledger.

## Revisions and iterations

- `revision` is a positive integer, displayed as `r1`, `r2`, etc. Increment
  once per meaningful saved update, including a status transition or new
  verification evidence. An unchanged repeat run does not increment it.
- `iteration` identifies delivery scope, for example `I01`, `I02`. A new
  invocation, clarification, correction, or bug fix is not automatically a
  new iteration. Increment when a new delivery scope is established.
- Normally keep iterations in the same canonical file. Record each
  iteration's goal, scope delta, criteria, status, and relationship to the
  previous iteration. Preserve previous completion/acceptance history.
- Split an iteration only when independent delivery or parallel maintenance
  needs it. Both files must identify parent matter, iteration, relationship,
  and canonical links; the parent must identify which scope is current.
  Do not invent a new independent requirement for an existing matter.
- Keep `template_version` separate: it identifies the DSL/schema, not the
  document revision or product iteration.

## Current content and history

Maintain identity, revision, iteration, created/updated times, current
status, related paths, current effective content, and append-only change
history. A project-native header/table is as valid as YAML frontmatter.

Update current content and history together. History entries include date,
revision, iteration, source/reason, concrete before/after changes, status
transitions, and verification/acceptance evidence when applicable. Preserve
original discovery and acceptance records; do not replace them with only
the latest conclusion. `vk/` is ignored by Git, so Git history alone cannot
provide this audit trail. Diffs can preserve detailed previous text without
creating a new report for every run.

Store test outputs/screenshots in linked `artifacts/` run directories when
needed. Timestamped evidence is allowed; competing narrative reports are
not. Full document snapshots are reserved for important baselines or an
explicit preservation request.

## Requirement and feature status

Use these states, or map them clearly to the project's existing vocabulary:

| State | Meaning / transition evidence |
| --- | --- |
| `awaiting_confirmation` | Scope or criteria need confirmation |
| `ready` | Current scope is agreed and ready to implement |
| `in_progress` | Implementation is underway |
| `completed_pending_acceptance` | Implementation and required verification passed; record results |
| `accepted` | User explicitly accepted, or an agreed acceptance mechanism passed; record who/mechanism, scope, time, result |
| `blocked`, `deferred`, `cancelled` | Record reason and remaining work or resumption condition |

- Track status for the overall requirement/current iteration and individual
  feature items. Partial implementation cannot make the whole requirement
  complete; blocked work must remain visible. Aggregate status from required
  items and criteria, not the most recently finished item.
- Every requirement/function adjustment, whether from the user, design,
  implementation, review, or acceptance feedback, must update the current
  requirement text, feature list, criteria, affected statuses, revision,
  and change history. Record removed scope with a reason rather than erasing
  it. Preserve the original request and log subsequent change requests.
- For a defect repair, add the repair summary and verification to the
  affected feature, linking the stable review finding for details. Pure
  internal changes need not invent a product requirement.
- On implementation completion, record actual behavior, evidence, baseline,
  and remaining gaps; set `completed_pending_acceptance` only when required
  checks passed. Commit/push, a clean review, and developer tests do not by
  themselves constitute product acceptance.
- On acceptance, update the requirement and feature states immediately in
  that task. Never infer acceptance merely from silence, a code change, or
  a request to submit.
- When accepted functionality changes, preserve the prior acceptance event
  and return only affected items to implementation/verification/acceptance.
  Unaffected accepted items remain accepted. A new delivery iteration has
  its own status; an earlier accepted iteration is not retroactively undone.
- Existing requirements must be synchronized even when no extra work/review
  report is needed. If a functional task has no requirement file, create a
  concise local requirement with goal, feature items, criteria, status,
  evidence, and history; do not force a full request DSL for a small repair.

## Review findings

- Give each finding a stable ID, for example `REQ-001/F-001`. Match by root
  cause and failing behavior; line movement or a rewritten title is not a
  new finding. Independently caused problems receive separate IDs.
- Preserve severity, original discovery/baseline, impact, current location,
  current status, repair details, verification, and status-change history.
- Lifecycle: `open` -> `in_progress` -> `fixed_pending_verification` ->
  `verified_resolved`. A failed fix or regression becomes `reopened` under
  the same ID with new evidence. `deferred` and `not_applicable` require
  reasons; neither counts as verified repaired.
- Code changes alone mean at most `fixed_pending_verification`. Close only
  after checking the reported failure and relevant regression behavior.
  Distinguish static evidence from executed tests and blocked checks.
- Review both new changes and relevant previous findings. For every old
  finding, record whether it was rechecked, the result, or `not rechecked`
  for this run. Omission is not resolution. Report new findings separately
  from unresolved old findings; "no new findings" is not "all resolved".
- Evidence identifies scope, date, commit, and dirty-worktree fingerprint
  or diff summary when applicable. Keep historical evidence after code
  changes, but do not present it as verification of the current baseline.
- `vk-work` writes repair details/status back to the canonical review and
  affected requirement. `vk-review` writes recheck results to the same
  finding and synchronizes affected requirement status/evidence. Review
  resolution is not automatic product acceptance.

## Safe updates and legacy documents

- Resolve identity before changing content. Preserve existing metadata,
  creation time, history, and links. Write atomically where a helper is used;
  validate before replacing a valid file. Avoid overwriting concurrent edits.
- For legacy files, adopt one canonical path after inspecting their content.
  Add identity/revision metadata and traceable source links as part of the
  next real update. Merge only clearly related records; conflicting scopes
  or statuses require clarification. Never infer resolution from file dates.
  Do not silently delete or rewrite the other historical files.
- Before declaring a task complete, check implementation, required checks,
  requirement synchronization, and linked review synchronization. If a
  document cannot be updated, report the completed code and outstanding
  documentation separately. Final replies identify updated paths,
  revisions, iteration/status, and remaining unverified work.
