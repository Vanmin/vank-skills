# Backend Code-Quality Rules

These rules adapt general maintainability guidance to backend application code.
They are applied while writing each slice, checked before the next slice, and
revisited during a bounded cleanup pass. They are quality guidance unless they
affect correctness, testability, or a declared business boundary.

## Readability and cognitive load

- Prefer guard clauses and early returns when they make the main path linear.
- Reduce deep nesting, long conditional chains, and `else` blocks after a return.
- Name functions by the business intent they provide, not by implementation steps.
- Keep one function at one abstraction level. Separate orchestration from SQL,
  serialization, logging, and other mechanics.
- Use domain nouns in names. Short names are fine in genuinely tight local scopes.
- Comments explain a non-obvious reason, invariant, or failed alternative. Rewrite
  comments that merely narrate the code.

## Types and single sources of truth

- Model finite states, event kinds, roles, and protocol codes with named types and
  constants. Make invalid transitions difficult to represent.
- Keep labels, safe messages, transport status, and other metadata for one finite
  concept in one canonical mapping. Do not maintain parallel maps across files.
- Validate external input once at the boundary. Inside the service, pass typed and
  validated values instead of repeating defensive checks.
- Prefer structured domain errors and explicit absence over sentinel strings or
  numbers. Preserve causes for logs without exposing them to clients.

## Reuse and abstraction

- Search neighbouring features and shared packages before adding a helper, type,
  formatter, constant, or error mapping.
- Reuse the existing semantic implementation when it is truly the same concept.
  Do not create a generic `utils` package for one call site.
- Avoid future-only configuration, wrappers, flags, or layers. Add an abstraction
  when it removes a current duplication or isolates a real boundary.
- Keep the new feature's file shape symmetrical with nearby features. A smaller
  diff is useful only when the resulting ownership and reading order are clearer.

## Pure core and testable shell

- Keep business decisions and state-transition calculations pure where practical.
- Keep database, RPC, clock, random, ID, and message side effects in a thin shell.
- Inject time, randomness, and ID generation when they affect business behavior or
  make deterministic tests difficult.
- Prefer explicit return values for expected business failures. Reserve panic/throw
  style behavior for programmer errors or unexpected infrastructure failures.

## Bounded simplification

Mechanical candidates may be applied one at a time after targeted tests pass:

- remove redundant `else` after return;
- flatten a safe nested guard;
- consolidate duplicated protocol constants or error mappings;
- rename an unambiguous local to its domain meaning;
- move a helper beside the canonical operation it serves.

Judgment-heavy changes stay as findings until the owner approves the direction:

- moving responsibilities between packages;
- changing repository/service interfaces;
- introducing a new abstraction or shared package;
- changing transaction, retry, or side-effect boundaries;
- broad file or module decomposition.

For every applied simplification: run the smallest relevant check, inspect the diff,
and revert the individual change if behavior or clarity regresses. Do not mix a broad
cleanup with a feature change.

## Findings

Use stable IDs:

- **CQ-001**: avoidable branching or nesting increases cognitive load;
- **CQ-002**: a function mixes responsibilities or abstraction levels;
- **CQ-003**: naming or comments hide business intent;
- **CQ-004**: finite concept has duplicated or parallel sources of truth;
- **CQ-005**: existing semantic logic was reimplemented;
- **CQ-006**: boundary value or expected failure is weakly typed;
- **CQ-007**: business logic is coupled to avoidable IO/time/randomness;
- **CQ-008**: abstraction or refactor expands scope without a present benefit;
- **CQ-009**: change lacks the targeted test needed to preserve behavior;
- **CQ-010**: mechanical simplification was applied without scoped verification.

Report evidence and impact. Do not promote a personal style preference to a blocking
finding.
