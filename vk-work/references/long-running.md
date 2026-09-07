# Long-running control and subagents

Load only when the task spans modules or cycles, or the user asked for
subagents, delegation, or automation.

## Controller

Act as controller + integrator. Keep a ledger:

- current objective
- in-scope files / modules
- excluded responsibilities
- cycle number
- last build / test result
- blockers
- next control decision

Loop: lock requirements → scoped implementation → compile → targeted
verify → control decision → safe auto-repair → re-verify.

Prefer short cycles. After each cycle, re-check scope, whether the failure
is deterministic, and whether the partition still holds.

Resume from `./vk/work/checkpoint.md` when it exists: read it, then verify
branch and `HEAD` against the recorded commit. Discard stale conclusions.

## Subagents

Use subagents only when all are true:

1. The user asked for subagents, parallel work, or long-running automation.
2. Work splits into disjoint write ownership.
3. Delegation will not block the critical-path decision.

Keep work local when the task is small, the next step needs the missing
result, writers would collide, or the design is still unclear.

Agent 0 keeps: requirement lock, architecture, shared contracts, build
strategy, integration, final verification.

Each slice must return touched files, summary, risks, and evidence.
Never overlap write ownership unless the user accepts merge risk.
Integrate centrally. The final answer must separate local vs delegated work.
