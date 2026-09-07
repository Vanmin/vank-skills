---
name: vk-ios-agents
description: Orchestrate Codex-based iOS app development by coordinating multiple local skills (especially Figma-to-code and SwiftUI skills) through dependency-aware execution. Use when requests involve end-to-end iOS delivery, multi-skill coordination, parallel workstreams, milestone planning, or converting Figma designs into production SwiftUI with staged validation.
---

# vk-ios-agents

## Shared Contract

- Load `../shared/vk-core-contract.md` before acting.
- Follow the shared result contract: start with a summary card, then structured body and Auto-evolution.
- Local records go under `./vk/ios-agents/`.
- For a real multi-skill delivery or a material gate decision, write plan, execution, and gate results to `./vk/ios-agents/`. Do not create a record for a brief intake, routing decision, or routine status update.
- `.gitignore` must include `vk/`.
- If records were staged by mistake: `git restore --staged -- vk/`.

## Overview

Use this skill as the top-level scheduler for iOS app work. It decides which skill to run, in what order, and which streams can run in parallel.

Load `references/orchestration-matrix.md` when selecting lanes and gates.

## Intake Contract

Collect or infer:
1. Product scope (MVP, feature, refactor, bugfix)
2. Design source (Figma URL/node IDs or no design)
3. Tech baseline (SwiftUI/UIKit, iOS minimum version, existing modules)
4. Constraints (deadline, accessibility, animation quality, CI/testing target)

If design inputs are missing for design-led requests, ask for Figma link/node IDs first.

## Skill Routing

Default skill set for Codex + Figma + iOS:
1. `figma`: read design context, tokens, assets, dimensions
2. `figma-implement-design`: convert selected nodes to implementation targets
3. `swiftui-expert-skill`: produce/adjust production SwiftUI code
4. `mobile-ios-design` + `apple-hig-designer`: align UX with iOS HIG
5. `swiftui-animation`: implement interactions and transitions
6. `accessibility-compliance`: apply WCAG/mobile accessibility checks
7. `screen-reader-testing`: validate VoiceOver flows when UI changes are significant

Skip skills that are not required by the request.

## Orchestration Model

Use a DAG-style plan, not a strict linear chain.

### Lane A: Discovery
- Read requirements and repository context
- Pull Figma context if provided
- Define acceptance criteria and checkpoints

### Lane B: UI Build
- Implement static UI and design tokens
- Map components to feature modules

### Lane C: Behavior & Quality
- Implement state/data flow and error states
- Add accessibility semantics and motion adjustments
- Add or update tests

Run Lane B and Lane C in parallel after Discovery unless blocked by unresolved component contracts.

## Gates

Do not move forward without passing each gate:
1. Design fidelity gate: spacing/typography/colors/components match intent
2. HIG gate: navigation, touch targets, platform patterns are native
3. Accessibility gate: labels, focus order, dynamic type, reduced motion
4. Engineering gate: build passes and tests are updated for changed behavior

## Execution Rules

1. Start with a short dependency plan identifying parallelizable tasks.
2. Prefer parallel execution when tasks touch different files or concerns.
3. Serialize when there is a shared contract risk (same view model/API/schema).
4. After each lane finishes, publish concise status and blockers.
5. If blockers appear, re-plan DAG edges instead of forcing a linear flow.

## Output Format

For each coordinated task, output:
1. Summary card titled `😁 + short task summary`, with status, scope, validation, and either the local record path or `not created — routine result`
2. `Plan`: lanes, dependencies, and gate criteria
3. `Execution`: what was done per lane and by which skill
4. `Validation`: gate results with concrete evidence
5. `Next`: remaining work or handoff
6. Auto-evolution: bad cases, external research, automation suggestion

If a coordination pattern repeatedly fails, or an upstream platform/design workflow changed, capture it under:
- `./vk/ios-agents/bad-cases/`
- `./vk/ios-agents/research/`
