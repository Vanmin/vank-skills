# Vank–gstack Delivery Bridge

Use this reference only from `vk-work` after its local build and targeted
verification gates. Vank remains the controller and the owner of durable
project records under `./vk/`; gstack supplies specialist execution where it
has a real advantage.

## Selection

Do not run gstack merely because it is installed. Select one or more of the
following gates only when their entry criteria are met and the corresponding
gstack skill is available in the current host.

| Entry criteria | gstack specialist | Vank responsibility |
| --- | --- | --- |
| A user-visible web flow changed, or a browser regression is plausible | `qa` / `browse` | Define the user journey; save result and evidence in `./vk/work/`. |
| Latency, throughput, or performance-regression risk is material | `benchmark` | Define the acceptance threshold and record the interpretation. |
| Auth, permissions, secrets, payments, PII, or privileged operations changed | `cso` | Keep `vk-restrict` data-flow and dependency gate; record remediation decisions. |
| User explicitly authorizes PR landing or deployment | `ship` or `land-and-deploy` | Preserve scope evidence and release decision; do not deploy without authorization. |
| A deployment occurred and user authorizes post-deploy observation | `canary` | Record the observation window, signals, and rollback owner. |

Follow the selected gstack skill in full. If its instructions conflict with
the user's explicit authorization boundary, stop at that boundary and report
the conflict.

## Ownership and non-duplication

- Vank owns requirements (`vk-request`), backend design constraints
  (`vk-restrict`), implementation control (`vk-work`), local evidence, and
  the default changed-code review (`vk-review`).
- gstack owns browser-driven QA, performance probing, specialist security
  review, and its release or post-deploy operations.
- Do not run both `vk-review` and gstack `review` on the same diff by default.
  Use a second review only when the user asks for an independent review angle.
- Choose exactly one command owner for commit and push. For a normal scoped
  submission, use `vk-submit`; for an explicitly authorized gstack release
  flow, let `ship` or `land-and-deploy` own its release actions after Vank has
  produced the scope and verification evidence.
- Do not hardcode paths to gstack, copy its scripts, or assume browser,
  deployment, cookie, or production credentials exist.

## Evidence handoff

Before invoking a selected gstack specialist, provide the minimum context it
needs: change scope, target environment, acceptance criteria, known risks,
and any safe test account or fixture supplied by the user.

After it returns, append a concise handoff to the current `./vk/work/` record:

- selected specialist and why it was selected;
- command or flow performed and outcome;
- evidence location or the reason evidence could not be captured;
- remaining risk, owner, and next action.

If no bridge gate matched, record that Vank-only verification was deliberate;
do not report gstack as skipped due to an error.
