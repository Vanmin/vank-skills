# VK Shared Contract

## 1. Selective Local Records

- When a local record is warranted, `vk-*` skill documents, review notes,
  execution summaries, bad cases, and research notes go under
  `./vk/<skill-key>/`.
- Naming stays split:
  - skill invoke name, directory name, and install shim name stay `vk-xxx`
  - records use `vk/xxx`
- `<skill-key>` is the skill name without the `vk-` prefix, for example:
  - `vk-request -> ./vk/request/`
  - `vk-read -> ./vk/read/`
  - `vk-skill-man -> ./vk/skill-man/`
- Suggested subdirectories:
  - `artifacts/`: script output and temporary analysis
  - `bad-cases/`: failures, misjudgments, regressions
  - `research/`: web research and external practice notes
- Treat records as local, untracked assets under the **target project's** `./vk/`. Do not write skill run records into the home directory, automation trees, or external volumes.
- Do not create a record merely because a skill ran. Before writing one, apply
  this policy:
  - **Record:** the user asks to preserve or hand off the result; the task makes
    a cross-module or architecture decision; it changes a data-flow, security,
    release, or operational risk boundary; it produces a reusable plan, DSL,
    roadmap, or review baseline; it finds a material defect, blocker, or bad
    case; or it needs to resume across sessions.
  - **Usually skip:** routine Q&A, status checks, short explanations, small
    code reads, a trivial single-scope edit with passing verification, and
    clean no-op checks.
  - **Direct deliverables are different:** when the user asks for a roadmap,
    DSL, article, report, or other file, create that requested deliverable even
    if no additional execution record is warranted.
- When no record is warranted, do not create an empty directory or placeholder
  file. State `not created — routine result` in the final result instead.
- If the target project still has legacy `vk-xxx/` record directories, migrate before writing:

```bash
VK_SKILLS_DIR="${VK_SKILLS_DIR:-$HOME/.codex/skills}"
for _migrate in \
  "${VANK_HOME:-$VK_SKILLS_DIR/vank}/vk-submit/scripts/migrate_vk_record_dirs.py" \
  "$VK_SKILLS_DIR/vk-submit/scripts/migrate_vk_record_dirs.py"
do
  if [[ -f "$_migrate" ]]; then
    python3 "$_migrate" --repo-root .
    break
  fi
done
```

- Migration rules:
  - move `vk-xxx/` to `vk/xxx/`
  - if the target file exists and matches, delete the old copy
  - if both exist and differ, keep the conflict and report it; never overwrite silently

## 2. Git Hygiene

- Primary ignore rule: `vk/`
- In ordinary target projects, also ignore legacy paths: `vk-*/`.
- Exception: do **not** add `vk-*/` in the Vank package source repository,
  identified by top-level `vk-*/SKILL.md` directories. That pattern would
  ignore the package's tracked child skills; use `vk/` there instead.
- Do not keep per-skill ignore rules such as `vk-read/`. Keep old folders out of git.
- If records were staged by mistake:

```bash
git restore --staged -- vk/
```

## 3. Selective Auto Evolution

- After each substantive skill run, check for:
  - failure or a blocker
  - repeated questions of the same kind
  - format rework
  - user correction
  - foreseeable repetitive manual work
- Act only when the signal is material enough to help a later task or avoid a
  repeat failure. Then do at least one of:
  - write `./vk/<skill-key>/bad-cases/`
  - write `./vk/<skill-key>/research/`
  - emit a Codex automation suggestion for later review

### 3.1 Bad Case Capture

- Suggested name: `bad-case-YYYYMMDD-HHMMSS-<slug>.md`
- Required fields: `context`, `expected`, `actual`, `root_cause`, `fix_strategy`, `guardrail`

### 3.2 Web Research

- Prefer primary sources for prompts, evals, automation, orchestration, and model limits.
- If a source is not official, label it as inference or industry reference.
- Suggested name: `research-YYYYMMDD-HHMMSS-<slug>.md`
- Required fields: `question`, `sources`, `signals`, `adopt`, `not_adopt`

### 3.3 Automation

- For repeating evolution work, prefer `::automation-update{...}` over a verbal reminder.
- Describe only the task, not the schedule or working directory.

## 4. Unified Result Contract

- Instruction files in this package are English.
- Spoken results follow the user's language unless a skill requires another language.
- Final results use this order:
  1. `Summary card`
  2. `Execution summary`
  3. `Key artifacts`
  4. `Validation / evidence`
  5. `Risks / next steps`
  6. `Auto-evolution`
- The summary card is a compact left-border Markdown quote block.
- Defaults:
  - short `>` lines
  - 4 to 6 metadata rows
  - no long sentences inside the card
- **Routine** answers (short Q&A, trivial verified edits): summary card, what
  changed or the answer, and verification when code changed. Skip empty
  Auto-evolution and empty artifact sections.
- **Material** answers: full six-section contract.
- Do not use rich HTML cards, wide tables, or ASCII tables unless the host renders them reliably and the user asked.
- Put overflow detail in `Execution summary` or `Key artifacts`.
- Do not title the card "Result card".
- Title format: `ordinary emoji + short task summary`.
- Use a Unicode emoji, default `😁`. Do not use kaomoji. Do not rotate kaomoji styles.
- Keep the title short and scannable, for example:
  - `😁 Unify vk local record layout`
  - `😁 Finish skill sync and contract checks`
  - `😁 Tighten Swift safety and performance gates`
- Suggested skeleton:

```md
> **😁 Short task summary**
> Skill: `vk-xxx`
> Status: `done | partial | blocked`
> Scope: `...`
> Output: `...`
> Validation: `pass | partial | fail`
> Record: `./vk/xxx/...`
```

- `Skill:` is the invoke name, such as `vk-work`.
- `Record:` is the artifact directory, such as `./vk/work/...`, or
  `not created — routine result` when the selective record policy did not
  warrant a file.

- If the host supports directives, you may append:
  - `::automation-update{...}`
  - `::code-comment{...}`
  - other host card directives
