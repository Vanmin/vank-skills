# Governance

Use this module to maintain the Vank **package**, not a random product repo.
Day-to-day skill hygiene still runs through [vk-skill-man](../vk-skill-man/SKILL.md).

## Shape

```text
vank/
  SKILL.md                 # router only
  shared/                  # vk-core-contract
  vk-question/ …           # full child skills
  scripts/install.sh       # one bundle link + vk-* shims
```

Children stay in this tree. Do not split them back into 13 installable
packages.

## Install

From this repository:

```bash
bash scripts/install.sh
```

That command:

1. Links this repo to `~/.codex/skills/vank`, `~/.claude/skills/vank`, and
   `~/.cursor/skills/vank`. Nested `vk-*` skills live inside that one
   directory, same as gstack.
2. Removes leftover host-root `vk-*` links that pointed at this repo or
   the old `legacy flat package` tree. Pass `--with-shims` only if a host cannot
   discover nested `SKILL.md` files.
3. Pins `vkpush` to `~/.local/bin/vkpush` when `vk-submit/scripts/vkpush`
   exists.

Uninstall shims and bundle links with `bash scripts/uninstall.sh`. It does
not delete this git repo.

## Maintenance loop

1. Inventory children, shared contract, scripts, and host links.
2. Remove or simplify only dead, duplicated, or misleading material after
   checking callers and installed links.
3. Capture real failures as bad cases under the target project's
   `./vk/skill-man/bad-cases/` (or this package's child `bad-cases/` when
   the failure is about the suite itself).
4. Prefer strengthening an existing child over adding a fourteenth skill.
5. After changing a child, re-run `bash scripts/install.sh` if link layout
   changed; otherwise a new session is enough.

## Hygiene

- Keep the router description short so hosts pick children by their own
  descriptions first.
- Keep child `name:` values as `vk-*` so existing `$vk-work` prompts work.
- Do not embed personal paths, credentials, or machine-specific examples
  in distributable files.
- Relative loads (`../shared/…`, `../vk-restrict/…`) must keep working
  from the nested child directory.
