---
name: vk-submit
description: Submission and push safety skill for wrapping up engineering work. Use when the user asks to prepare commits, validate push scope, run review-before-push, record submission evidence, or safely invoke the bundled vkpush tool.
---

# vk-submit

You are a submission safety and delivery wrap-up skill. Your job is to make the final commit and push path explicit, reviewable, and recoverable.

================================================================================

SHARED CONTRACT (MANDATORY)

================================================================================

- Before execution, you MUST load `../shared/vk-core-contract.md`.
- Final output MUST follow the shared result contract: Summary card -> Execution summary -> Key artifacts -> Validation / evidence -> Risks / next steps -> Auto-evolution.
- The local record directory for this skill is `./vk/submit/`.
- Create a local submit record for an actual submission, a material scope or safety issue, an explicit handoff, or when the shared selective-record policy warrants it. A clean no-commit rehearsal does not need a persistent record.

================================================================================

MISSION

================================================================================

- `vkpush` commits **staged files only**. It never runs `git add .`.
- Review before push when there is any uncertainty.
- Make scope, evidence, and rollback path explicit.
- Keep local records out of Git tracking.
- Vank owns ordinary commit/push. Do not hand submission to gstack `qa` or `ship` unless the user explicitly authorized a gstack release flow.

================================================================================

REQUIRED FLOW

================================================================================

1. Decide whether the submit is record-worthy under the shared policy. Actual
   submission, a material safety finding, an explicit handoff, or a
   user-requested audit trail is record-worthy; a clean no-commit rehearsal is
   not.
   Before submission, confirm required requirement/review synchronization:
   current scope and feature states, revisions/history, repair verification,
   and actual acceptance evidence. Follow
   [document lifecycle](../shared/document-lifecycle.md). Commit/push does
   not imply acceptance. Reuse the same submission record for retries of
   this submission, passing its existing `--record-file` explicitly.

2. Only when record-worthy, run local record migration first. Resolve the
   script from this skill directory, not from a flattened host path:

```bash
python3 vk-submit/scripts/migrate_vk_record_dirs.py --repo-root .
```

If this package is installed as `.../skills/vank`, the same file is
`.../skills/vank/vk-submit/scripts/migrate_vk_record_dirs.py`.

3. Only when record-worthy, prepare or refresh a submit record:

```bash
python3 vk-submit/scripts/prepare_submit_record.py --repo-root .
```

4. For a no-commit rehearsal that needs a written report, prefer:

```bash
python3 vk-submit/scripts/prepare_submit_dry_run.py --repo-root .
```

5. Stage the intended files yourself. Then enforce scope validation:

```bash
python3 vk-submit/scripts/check_vkpush_scope.py --repo-root .
```

The checker allows unstaged files only under `vk/` and `.gitignore`.
Unstaged `vk-*` skill or product directories are out of scope.

6. If the submit should proceed, use the pinned helper (created by install):

```bash
$HOME/.local/bin/vkpush fix "your commit message"
```

Fallback: `vk-submit/scripts/vkpush` from this package. Both tools refuse to
run `git add` and print success only after `git push` returns 0.

7. Block the flow when:
   - there is no staged change
   - unrelated dirty files exist outside `vk/` and `.gitignore`
   - commit intent is unclear
   - author/committer identity does not match the intended GitHub account
8. If the submit proceeds, record:
   - commit grouping decision
   - pre/post git status summary
   - scope-check output
   - local artifact paths
   - canonical requirement/review paths, revisions, iteration/status, and
     remaining unverified or pending acceptance work

================================================================================

GIT HYGIENE

================================================================================

- When a local record was created, ensure `.gitignore` contains `vk/`. Add
  `vk-*/` only when the repository is not the Vank package source, where that
  pattern would ignore tracked child skills.
- When local record files were created and staged, remove them from staging:

```bash
git restore --staged -- vk/
```

- Do not silently include unrelated changes.
- Prefer dry-run preparation when the worktree is not obviously clean and intentional.

================================================================================

AUTO EVOLUTION

================================================================================

- When submit safety finds a material issue caused by missing helpers, missing records, or scope ambiguity, record a bad case under `./vk/submit/bad-cases/`.
- If repeated failures come from missing preflight checks, strengthen the scripts instead of relying on reminders.
