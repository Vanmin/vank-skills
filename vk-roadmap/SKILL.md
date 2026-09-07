---
name: vk-roadmap
description: Read the architecture of a directory, analyze module duties and feature flows, and write a roadmap under the target project's `./vk/roadmap/`. Use when the agent must understand a codebase or subdirectory, summarize modules plus features, or sync a roadmap summary into `AGENTS.md` if one exists.
---

# VK Roadmap

## Shared Contract

- Load `../shared/vk-core-contract.md` before acting.
- Follow the shared result contract: start with a summary card, then structured body and Auto-evolution.
- Local records go under `./vk/roadmap/` in the target project.
- After generating a roadmap, write the document under that project's `./vk/roadmap/`.
- If a global `AGENTS.md` exists, try to sync a short summary into the managed block.
- `.gitignore` must include `vk/`. If records were staged by mistake: `git restore --staged -- vk/`.

## Inputs

Lock these before acting:

1. `target_dir`
   - Directory the user named.
   - Repo root: map the whole project.
   - Subdirectory: focus on that tree and its direct dependencies.
2. `analysis_goal`
   - Default: read architecture, analyze features, write a roadmap.
   - Extra organization (by module / phase / priority / risk) must appear in the document.
3. `scope_boundary`
   - Read-only analysis plus docs. Do not change product code by default.
   - Allowed writes: `./vk/roadmap/*` and the skill-managed block in `AGENTS.md`.

## Artifacts

Default file:

- `./vk/roadmap/roadmap-YYYYMMDD-HHMMSS.md`

Suggested structure:

1. Project / directory overview
2. Architecture overview
3. Feature domains
4. Module-to-duty map
5. Key flows
6. Roadmap suggestions
7. Risks / open questions
8. Next steps

If a global `AGENTS.md` exists, write a short summary into:

- start: `<!-- vk-roadmap:start -->`
- end: `<!-- vk-roadmap:end -->`

## Workflow

### Step 1: Scope lock

- Resolve `target_dir` to an absolute path.
- Stop if the directory is missing.
- Classify: single module, subsystem, or repo root.
- Include: tree, entry points, key config, module deps, feature flows.
- Exclude: generated output, huge binaries, vendor / cache / build.

### Step 2: Architecture reading

- Prefer `rg --files`, `find`, `tree` when present.
- Read entries, routes/handlers/controllers/services/models, core config, build/package files, existing `README.md`, `AGENTS.md`, design docs.
- For large trees, first take top-level dirs, key files per layer, obvious entries, dependency edges.

### Step 3: Feature analysis

- Infer feature domains from code and docs, not from the directory tree alone.
- Cover: what each module does, which modules form one capability, infra vs business, high coupling or unclear ownership.
- Missing evidence is `TBD`, not a fact.

### Step 4: Roadmap synthesis

- Merge directory architecture with feature capability into one actionable roadmap.
- Include current structure, capability map, cleanup/evolution items, staged actions.
- Default order when the user did not specify: foundations, core business, supporting toolchain, evolution ideas.

### Step 5: Write docs

- Create `./vk/roadmap/` under the target.
- Filename `roadmap-YYYYMMDD-HHMMSS.md`.
- Before write: migrate legacy `vk-*` record dirs per the shared contract; `.gitignore` covers `vk/` and `vk-*/`.
- If `vk/` was staged: `git restore --staged -- vk/`.

### Step 6: Global AGENTS sync

- Walk up from `target_dir` to the repo root and use the first global `AGENTS.md`.
- If found, run `scripts/sync_roadmap_to_agents.py` and update the `vk-roadmap` managed block only.
- If missing, report that and still finish the roadmap.

## AGENTS sync script

```bash
python3 <skill-dir>/scripts/sync_roadmap_to_agents.py --target-dir <target_dir> --roadmap-file <roadmap_file>
```

The script locates `AGENTS.md`, writes a compact summary into the managed block, and leaves other content alone.

## Quality bar

- Not a directory dump.
- Not a feature list dump.
- Architecture and duties must combine into a roadmap.
- The doc must be scannable, handoff-ready, and evolvable.
- Missing evidence is labeled `TBD`.

## Final response

1. Summary card
2. Execution summary
3. Key artifacts
4. Validation / evidence
5. Risks / next steps
6. Auto-evolution

Always state: target directory, roadmap path, whether `AGENTS.md` was updated, key architecture conclusions, key feature conclusions, remaining TBD.
