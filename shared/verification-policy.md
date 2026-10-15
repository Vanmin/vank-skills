# Proportionate verification and bounded repair

Before a review, retry, test run, or specialist handoff, identify what changed,
the concrete uncertainty, usable prior evidence, and the decision the next
action should resolve. Choose the smallest sufficient check:

| Choice | When | Action |
| --- | --- | --- |
| Reuse | Relevant scope/code/environment and prior conclusions still apply | Cite source evidence and impact assessment; do not claim a new run |
| Targeted | Local change or known failure with bounded impact | Review changed behavior/dependencies; run affected cases |
| Broader | Shared contracts, integration, high-risk boundaries, new failures, required project checks, or explicit user scope justify it | Name the boundary/risk and expand only enough to address it |

Documentation-only edits usually need relevant instruction/link/format
checks. Fixes need their reproducer and affected regressions. Do not run all
tests, validate every skill, invoke every specialist, or reread the whole
project merely because a new edit, skill invocation, phase, or submission
started. Lifecycle gates remain required; they do not require full reruns.

One review pass per scope is the default. Re-review only changed behavior,
affected findings, or newly evidenced risks. After sufficient checks pass,
hand off; do not commission more reviews for reassurance. Record unrelated
suggestions for separate scope instead of auto-fixing them into another
review -> refactor -> review chain. Honor checks required by the project.
Choose a finite check/repair plan for the current slice before entering a
loop; do not silently replenish it as new suggestions appear. If findings
keep shifting without approaching the agreed criteria, stop and report the
scope/design uncertainty rather than expanding into endless new repairs.

## Bounded repair

- Default to at most **two automatic repair attempts** for the same failure/
  root cause and affected scope. Each needs a concrete hypothesis, in-scope
  change, and targeted verification. A user/project may set a different
  finite limit before the cycle; never invent an unlimited extension.
- Stop earlier when the failure repeats without narrowing its cause or
  gaining evidence. Do not rerun unchanged deterministic failures. Confirmed
  missing dependencies, permissions, services, or decisions are blockers.
- A plausibly transient failure permits one evidenced retry, unless an
  existing finite project retry policy applies. Otherwise diagnose or stop.
- Keep the count with the stable issue/root cause in existing history or
  checkpoint. Changing skills, agents, wording, sessions, or restarting a
  process does not reset it. Do not chain tool-specific retry allowances.
- At the limit/no-progress condition, stop automatic repair and preserve
  attempted fixes, evidence, remaining uncertainty, and the next concrete
  decision/input needed. Report incomplete/blocked status; do not weaken
  criteria or mark checks passed. Independent authorized work may continue.
- Resume that repair only with new external evidence, a resolved blocker,
  or explicit user direction; define another finite scope/limit first.
  Waiting for acceptance is a handoff, not a polling/review loop.

## Keep context small

Read current metadata/ledger, latest relevant evidence, and affected findings
first. Retrieve older history/diffs only for a specific question. Do not
repeatedly print full documents with embedded histories, templates, repos,
or verbose passing logs into model context. Reuse references already read
in the task unless they changed.

Record meaningful verification choices/reasons and repair counts briefly in
existing events/issues/checkpoint. Do not create a new report or mandatory
schema fields per decision. Append real runs only when executed; explicitly
identify carried-forward evidence and its unchanged-impact rationale. Run
the cheap lifecycle gate once for changed state; reuse unchanged handoffs.
Acceptance/document-only events do not automatically retest unaffected code.
