---
name: vk-diagram-guard
description: Gate and repair flowchart assets in a writing-project article directory. Use when diagrams are black blocks, clipped, missing, imported incorrectly, or stuck on a 45x13 placeholder. Rebuilds mermaid diagrams, wraps SVG, drops unfixable refs, and writes a gate report.
---

# vk-diagram-guard

## Shared Contract

- Load `../shared/vk-core-contract.md` before acting.
- Follow the shared result contract: start with a summary card, then structured body and Auto-evolution.
- Local records go under `./vk/diagram-guard/`.
- `assets/diagrams/diagram_guard_report.json` remains the required gate output. Write a separate local summary or evolution note only for a material repair, blocker, or reusable bad case.
- `.gitignore` must include `vk/`.
- If records were staged by mistake: `git restore --staged -- vk/ 'vk-*'`.

## Overview

Quality-gate `assets/diagrams` for a single article directory and auto-fix what can be fixed so black blocks, clipped images, and placeholders do not ship.

## Workflow

1. Identify the target article directory (one article, not a tree of articles).
2. Scan `.md` files for flowchart refs: `assets/diagrams/diagram-*`.
3. Run the gate.
4. Enable auto-fix (prefer `gate-fix`).
5. Re-check and write `assets/diagrams/diagram_guard_report.json`.

## Gate checks

- Referenced file exists.
- PNG size is readable.
- PNG is not a placeholder (`45x13` or `<=60x20`).
- PNG meets the minimum size (default `120x40`).
- SVG has no `foreignObject` (avoids local black-block rendering).

Details: `references/gate-rules.md`.

## Auto-fix

- SVG with `foreignObject`: wrap as PNG-backed SVG when a sibling PNG exists.
- Missing/placeholder/tiny PNG: rebuild PNG and wrapper SVG from the same-name `.mmd` via `mmdc`.
- Still unfixable: optionally `--drop-unfixable-refs` to remove the Markdown image ref.

Mermaid size profiles: `references/diagram_profiles.json`.

## Scripts

### Main

`scripts/diagram_guard.py`

```bash
# gate + auto-fix + recheck
~/.codex/skills/vank/vk-diagram-guard/scripts/diagram_guard.py \
  --article-dir "/path/to/article-dir" \
  --mode gate-fix \
  --drop-unfixable-refs

# check only
~/.codex/skills/vank/vk-diagram-guard/scripts/diagram_guard.py \
  --article-dir "/path/to/article-dir" \
  --mode check
```

### Wrapper

`scripts/run_diagram_guard.sh`

```bash
~/.codex/skills/vank/vk-diagram-guard/scripts/run_diagram_guard.sh \
  "/path/to/article-dir" \
  --mode gate-fix \
  --drop-unfixable-refs
```

## Preconditions

- Local `python3`, `sips`, `npx`.
- Mermaid rebuild uses `@mermaid-js/mermaid-cli` via `npx`.
- Default renderer is Microsoft Edge:
  `/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge`
  Override with `--edge-path`.

## Output

Report:

1. `before` issue count
2. `after` issue count
3. `passed=true/false`
4. report path: `assets/diagrams/diagram_guard_report.json`
5. local record, when warranted: `./vk/diagram-guard/...`; otherwise `not created — routine result`

Final reply: summary card titled `😁 + short task summary`, then Execution summary, Key artifacts, Validation / evidence, Risks / next steps, Auto-evolution.

New failure modes or repeated manual work go under `./vk/diagram-guard/bad-cases/` and `research/`, plus `::automation-update{...}` when periodic.

Gate failure exit code is `2`.
