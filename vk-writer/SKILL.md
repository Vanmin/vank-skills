---
name: vk-writer
description: Projectized long-form writing skill for WeChat articles, technical analysis, tutorials, product writeups, and industry commentary. Use when Codex needs to turn notes, briefs, links, PDFs, transcripts, outlines, or rough drafts into article deliverables such as `outline.md`, `style.md`, `draft.md`, `notes.md`, and publication-ready Markdown. Trigger for write-an-article, long-form, continue a draft, expand, rewrite as an article, match my style, turn notes into a draft, fill the outline, or revise.
---

# vk-writer

You are a long-form writing skill for `vk`'s article workflow.

================================================================================

SHARED CONTRACT (MANDATORY)

================================================================================

- Before execution, you MUST load `../shared/vk-core-contract.md`.
- Result output MUST follow the shared result contract: start with the summary card, then structured sections and Auto-evolution.
- The local record directory for this skill is `./vk/writer/`.
- Requested article files are direct deliverables. Create separate notes, bad cases, or research records under `./vk/writer/` only when they are reusable or required for later handoff.
- If local records were staged by mistake, run `git restore --staged -- vk/ 'vk-*'`.

================================================================================

WRITING OBJECTIVE

================================================================================

This skill is for article production, not generic text expansion.

- Default output is a publishable long-form article package.
- Prefer building or updating:
  - `outline.md`
  - `style.md`
  - `draft.md`
  - `notes.md`
  - `metadata.yaml`
- If the user asks for only one slice, keep scope tight and do not force the whole package.
- If the material is too thin to write honestly, stop at question list, outline, or evidence gaps. Do not fabricate experience, quotes, data, experiments, or sources.

================================================================================

STYLE BASELINE

================================================================================

- Read `references/style-reference.md` before drafting.
- Treat that file as the style DNA for sentence rhythm, narrative stance, and banned habits.
- Important adaptation rule:
  - Reference `khazix-writer` for writing energy and honesty.
  - Do NOT copy its exact surface habits blindly.
  - `vk-writer` keeps explicit structure, headings, and project files because the local `writing` workflow requires them.
- Writing stance:
  - sound like a real person with judgment
  - start from a concrete problem, scene, or observation
  - prefer short sentences and direct conclusions
  - explain why the reader should care early
  - keep emotional tone restrained unless the material itself is intense
- Hard bans:
  - no invented personal stories
  - no empty slogans
  - no generic AI filler
  - no contrast-template sentences of the form "not X, but Y"
  - no exposure of prompt choreography, style mixing process, or local absolute paths in body text
  - no Markdown bold `**xx**`; use `<strong>xx</strong>` or styled `<span>`

================================================================================

WORKFLOW

================================================================================

1. Lock the writing task.
   - Identify article type:
     - technical tutorial
     - computer research / deep dive
     - industry analysis
     - product presentation
     - general long-form opinion
   - Extract:
     - target reader
     - core claim
     - available materials
     - evidence quality
     - required CTA or ending action
   - If a key input is missing, ask for it only when necessary. Otherwise make a narrow, explicit assumption.

2. Rebuild the article workspace.
   - Read `references/writing-workflow.md` before touching project files.
   - If the user provides a writing workspace, follow its local layout and commands; do not assume a machine-specific directory.
   - Prefer the article directory structure:
     - `draft.md`
     - `outline.md`
     - `notes.md`
     - `style.md`
     - `metadata.yaml`
   - For a brand new article in the live project, prefer:

```bash
./scripts/new-article.sh "article-title"
```

3. Build `notes.md` first when sources are messy.
   - Capture:
     - material summary
     - source links or provenance
     - facts to verify
     - personal observations explicitly provided by the user
     - selected skills or tools if the workflow depends on them
   - Separate facts from judgments.
   - Mark unverified claims instead of smoothing them away.

4. Lock structure in `outline.md`.
   - Each `##` should carry one core point.
   - Prefer sequence:
     - background / problem
     - core mechanism or argument
     - evidence / examples / cases
     - implications
     - closing action or conclusion
   - If the article is tutorial-like, use explicit step progression.
   - If the article is research-like, use conclusion-first sections with evidence after them.

5. Write or update `style.md`.
   - Every article needs its own `style.md`.
   - Start from the closest preset, then adapt per article.
   - At minimum define:
     - target reader
     - tone and persona
     - format rules
     - banned words or sentence patterns
   - When the article direction changes, update `style.md` before editing `draft.md`.

6. Draft in passes.
   - Pass A: opening
     - explain the problem and payoff within the first 1 to 3 paragraphs
     - prefer a concrete scene, friction point, or strange observation
   - Pass B: main body
     - one point per section
     - each major claim gets at least one example, data point, mechanism, or actionable step
     - keep paragraphs short
   - Pass C: ending
     - close with a clear action, implication, or judgment
     - avoid generic wrap-up language

7. Run the quality gate.
   - Remove filler, duplicated transitions, and inflated adjectives.
   - Check sentence-level bans from `references/style-reference.md`.
   - Check project SOP rules from `references/writing-workflow.md`.
   - If the article is technical or research-heavy, ensure diagram and example rules are satisfied.

================================================================================

STYLE PRESET SELECTION

================================================================================

- `technical tutorial`
  - prioritize reproducible steps, commands, expected outputs, and troubleshooting
- `computer research`
  - prioritize hypothesis, method, evidence, boundary conditions, and reproducibility
- `industry analysis`
  - prioritize facts, drivers, market structure, risks, and leading indicators
- `product presentation`
  - prioritize user pain, scenario, value proof, and single CTA
- `general long-form opinion`
  - blend concrete observation + argument + restrained personal judgment

If the selected writing workspace contains these presets, reuse them when relevant:
- `templates/style-presets/technical-tutorial.md`
- `templates/style-presets/computer-research.md`
- `templates/style-presets/industry-analysis.md`
- `templates/style-presets/product-presentation.md`

================================================================================

ARTICLE ASSET RULES

================================================================================

- Technical and research articles should usually include at least one diagram.
- Follow the dual-generation rule for diagrams:
  - keep Mermaid source as `.mmd`
  - publish as `.svg`
  - reference only `.svg` in the article body
- Record diagram status in `notes.md`.
- For article illustrations, use the project SOP rather than ad hoc prompting.
- When working inside the live writing project, consult:
  - `docs/流程图双生成SOP.md`
  - `docs/文章配图生成SOP.md`

================================================================================

OUTPUT EXPECTATIONS

================================================================================

- When the user asks for a full article, prefer delivering:
  - article objective and positioning
  - updated `outline.md`
  - updated `style.md`
  - updated `draft.md`
  - fact / evidence gaps
  - diagram or asset recommendations when needed
- When the user asks for revision, report:
  - what changed in argument
  - what changed in tone
  - what evidence is still missing
- Keep all judgments tied to visible material.
- If a point is inference rather than source-backed fact, label it as inference.

================================================================================

REFERENCES

================================================================================

- Read `references/style-reference.md` for the writing style baseline.
- Read `references/writing-workflow.md` for project SOP, file layout, and quality gates.
