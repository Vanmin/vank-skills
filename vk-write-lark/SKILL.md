---
name: vk-write-lark
description: Sync a local article directory to Lark/Feishu from a natural-language request. Stable scope is preflight + asset manifest + blockers + an executable sync plan. Perform a real cloud write only when the runtime has Lark write tools and the destination is explicit.
---

# vk-write-lark

## Shared Contract

- Load `../shared/vk-core-contract.md` before acting.
- Follow the shared result contract: start with a summary card, then structured body and Auto-evolution.
- Local records go under `./vk/write-lark/`.
- Write preflight results, asset maps, blockers, or apply records to `./vk/write-lark/` only when the result will be handed off, a cloud write occurs, a material blocker is found, or the shared selective-record policy warrants it.
- `.gitignore` must include `vk/`.
- If records were staged by mistake: `git restore --staged -- vk/`.

## Overview

Turn local article body, titles, images, and diagrams into Lark-ready input. Run readiness / scope / target checks before any write.

This skill is still a governance front-end. It must not fake a cloud success or reuse another skill's semantics.

## Stable scope

- `preflight`: article dir, main Markdown, image/diagram assets, title, destination.
- `manifest`: files to sync, target doc, strategy, blockers, human confirmations.
- `apply`: only when the runtime exposes Lark write tools and the user named the doc/wiki/token and create-vs-update choice.

If write tools or destination are missing, stop at `manifest`.

## Workflow

1. Identify the article directory and whether the scope is `outline`, `style`, `draft`, or the full article.
2. Locate the main Markdown and attachments. Split source files, local-only notes, and assets that need upload.
3. Preflight:
   - body exists and is non-empty
   - diagrams should pass `vk-diagram-guard` first
   - updates need a document id and replace range
4. Produce the plan: source files, target doc/wiki/folder, create-vs-update, blockers.
5. Apply only when tools and destination are sufficient; otherwise give the next executable step.

## Required inputs

- Source article or project directory
- Scope: `outline | style | draft | full-article`
- Mode: `create-new-doc | update-existing-doc`
- For a real write: target id, overwrite permission, and a live Lark tool

## Guardrails

- Do not claim sync success without a tool receipt.
- Do not pretend `vk-diagram-guard` scripts are this skill.
- Unclear destination blocks `apply`; emit `manifest` first.
- Unstable assets or ungated diagrams: fix the source first.
- Conservative default: create a new doc, or replace only an explicit block.

## Current package state

- No stable dedicated write script ships in this repo.
- Prefer the runtime's Lark connector or MCP. If none is present, this skill only checks, inventories, and plans.
- The stable promise is sync governance, not a finished cloud writer.

## Output

1. readiness: `ready | blocked | partial`
2. source scope
3. target mode and destination
4. blockers / risks / confirmations
5. local record, when warranted: `./vk/write-lark/...`; otherwise `not created — routine result`

Final reply: summary card titled `😁 + short task summary`, then Execution summary, Key artifacts, Validation / evidence, Risks / next steps, Auto-evolution.

New mapping mistakes or repeated manual work go under `./vk/write-lark/bad-cases/` and `research/`, plus `::automation-update{...}` when periodic.
