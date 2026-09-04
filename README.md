# Vank

Vank is a gstack-style skill suite: **one git repo, one install, many child skills**.

The root [`SKILL.md`](SKILL.md) is only a router. Nested `vk-*` directories hold the real workflows (question, read, roadmap, request, restrict, work, review, submit, writer, iOS, diagrams, Lark, skill hygiene).

- English: this file
- Chinese: [README.zh-CN.md](README.zh-CN.md)

## Layout

```text
vank/
  SKILL.md                 # router ($vank)
  shared/vk-core-contract.md
  vk-question/ ...         # child skills
  scripts/install.sh
  README.md
  README.zh-CN.md
```

Child `name:` values stay `vk-*`, so `$vk-work` remains valid. `$vank` only routes; `$vk-work` executes.

## Install

From this repository:

```bash
bash scripts/install.sh
```

That command:

1. Symlinks this repo to `~/.codex/skills/vank`, `~/.claude/skills/vank`, and `~/.cursor/skills/vank`.
2. Leaves children nested inside the bundle so hosts can discover them the same way they discover gstack skills.
3. Removes leftover host-root `vk-*` shims that pointed at this repo.
4. Pins `vkpush` to `~/.local/bin/vkpush` when `vk-submit/scripts/vkpush` exists.

Dry run:

```bash
bash scripts/install.sh --dry-run
```

If a host does not recurse into nested `SKILL.md` files:

```bash
bash scripts/install.sh --with-shims
```

Uninstall links (does not delete this git repo):

```bash
bash scripts/uninstall.sh
```

Optional env vars: `CODEX_SKILLS_DIR`, `CLAUDE_SKILLS_DIR`, `CURSOR_SKILLS_DIR`, `AGENTS_SKILLS_DIR`, `LOCAL_BIN_DIR`.

Open a **new agent session** after install so the host reloads skills.

## Usage

| You say | What runs |
| --- | --- |
| `$vank` / "use vank" | Router picks a child, then follows that child's `SKILL.md` in full |
| `$vk-work`, `$vk-request`, … | Named child, skip the router |
| `/vk-review` in Claude Code | Same as `$vk-review` |

Do not treat the routing table as a substitute for a child skill.

Typical sequence (skip finished phases):

```text
question / read / roadmap → request → restrict → work → review → submit
```

Specialists (`vk-writer`, `vk-ios-agents`, `vk-diagram-guard`, `vk-write-lark`) load only when that domain is present.

### Optional gstack delivery gates

For non-trivial implementation, `vk-work` remains the controller and reads the
[Vank–gstack delivery bridge](references/gstack-bridge.md). It calls an
installed gstack specialist only when the task needs browser QA, performance
evidence, security review, or an authorized release. It does not copy gstack,
run the whole suite, or duplicate Vank's backend constraints and local records.

### Children

| Skill | Use when |
| --- | --- |
| `vk-question` | Concepts, trade-offs, Q&A |
| `vk-read` | Read-only code tracing |
| `vk-roadmap` | Repository or module map |
| `vk-request` | Intent → executable DSL |
| `vk-restrict` | Backend data / IO / dependency gates |
| `vk-work` | Implement, repair, long-running delivery |
| `vk-review` | Diff review and risk |
| `vk-submit` | Commit, push, `vkpush` |
| `vk-writer` | Long-form article package |
| `vk-ios-agents` | iOS multi-skill orchestration |
| `vk-diagram-guard` | Diagram asset gate and repair |
| `vk-write-lark` | Local docs → Lark plan (write only when tools and target are clear) |
| `vk-skill-man` | Maintain this package / local skill hygiene |

## Records

Skill run records belong in the **target project**, not in this package:

- `./vk/<skill-key>/` (for example `vk-work` → `./vk/work/`)
- Ignore `vk/` in that project's `.gitignore`

Optional durable project context: `./vank/context|specs|decisions|status/`. See [references/contract.md](references/contract.md).

## Package maintenance

Day-to-day hygiene: `$vk-skill-man`. Shape and install policy: [references/governance.md](references/governance.md).
