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

- Never assume the bundled `vkpush` tool only submits staged changes.
- Review before push when there is any uncertainty.
- Make scope, evidence, and rollback path explicit.
- Keep local records out of Git tracking.

================================================================================

REQUIRED FLOW

================================================================================

1. Decide whether the submit is record-worthy under the shared policy. Actual
   submission, a material safety finding, an explicit handoff, or a
   user-requested audit trail is record-worthy; a clean no-commit rehearsal is
   not.

2. Only when record-worthy, run local record migration first:

```bash
python3 scripts/migrate_vk_record_dirs.py --repo-root .
```

3. Only when record-worthy, prepare or refresh a submit record:

```bash
python3 scripts/prepare_submit_record.py --repo-root .
```

4. For a no-commit rehearsal that needs a written report, prefer:

```bash
python3 scripts/prepare_submit_dry_run.py --repo-root .
```

5. Before any real submit action, enforce scope validation with:

```bash
python3 scripts/check_vkpush_scope.py --repo-root .
```

6. If the submit should really proceed, prefer the fixed absolute-path tool created by quick start:

```bash
$HOME/.local/bin/vkpush fix "your commit message"
```

If `scripts/quick_start.sh` has already completed, this absolute path will be fixed to the synced skill tool. After namespace initialization, both the binary name and absolute path suffix will be renamed together with the chosen prefix.

7. Block the flow when:
   - there is no staged change
   - unrelated dirty files exist outside `vk/`, `vk-*`, and `.gitignore`
   - commit intent is unclear
8. If the submit proceeds, record:
   - commit grouping decision
   - pre/post git status summary
   - scope-check output
   - local artifact paths

================================================================================

GIT HYGIENE

================================================================================

- When a local record was created, ensure `.gitignore` contains `vk/`. Add
  `vk-*/` only when the repository is not the Vank package source, where that
  pattern would ignore tracked child skills.
- When local record files were created and staged, remove them from staging:

```bash
git restore --staged -- vk/ 'vk-*'
```

- Do not silently include unrelated changes.
- Prefer dry-run preparation when the worktree is not obviously clean and intentional.

================================================================================

AUTO EVOLUTION

================================================================================

- When submit safety finds a material issue caused by missing helpers, missing records, or scope ambiguity, record a bad case under `./vk/submit/bad-cases/`.
- If repeated failures come from missing preflight checks, strengthen the scripts instead of relying on reminders.
