#!/usr/bin/env python3
"""Conservative auto-evolution for local vk-* skills.

Scope:
- Discover vk-* skills by folder name + SKILL.md.
- Auto-regenerate agents/openai.yaml when missing or stale.
- Validate each processed skill with quick_validate.py.

This script intentionally avoids high-risk content rewrites.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

SOURCE_ROOT = Path(__file__).resolve().parents[2]
CODEX_SKILLS_DIR = Path(
    os.environ.get("CODEX_SKILLS_DIR", Path.home() / ".codex" / "skills")
).expanduser()
SKILL_CREATOR_DIR = Path(
    os.environ.get("SKILL_CREATOR_DIR", CODEX_SKILLS_DIR / ".system" / "skill-creator")
).expanduser()
GEN_OPENAI_YAML = SKILL_CREATOR_DIR / "scripts" / "generate_openai_yaml.py"
QUICK_VALIDATE = SKILL_CREATOR_DIR / "scripts" / "quick_validate.py"


@dataclass
class SkillResult:
    path: Path
    status: str
    reason: str


def expand_roots(roots: Iterable[str]) -> List[Path]:
    seen = set()
    out: List[Path] = []
    for root in roots:
        p = Path(root).expanduser().resolve()
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return out


def discover_skills(roots: List[Path], prefix: str) -> List[Path]:
    found = set()
    for root in roots:
        if not root.exists():
            continue
        for skill_md in root.rglob("SKILL.md"):
            skill_dir = skill_md.parent.resolve()
            if skill_dir.name.startswith(prefix):
                found.add(skill_dir)
    return sorted(found)


def clean_scalar(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_simple_mapping(block: str) -> Dict[str, str]:
    data: Dict[str, str] = {}
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = clean_scalar(value)
    return data


def read_frontmatter(skill_md: Path) -> Dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md is missing valid frontmatter")
    data = parse_simple_mapping(match.group(1))
    if not data:
        raise ValueError("frontmatter is not a mapping")
    return data


def generate_openai_yaml(skill_dir: Path, skill_name: str, dry_run: bool) -> Tuple[bool, str]:
    default_prompt = f"Use ${skill_name} for this task and follow the skill contract."
    cmd = [
        "python3",
        str(GEN_OPENAI_YAML),
        str(skill_dir),
        "--interface",
        f"default_prompt={default_prompt}",
    ]
    if dry_run:
        return True, "dry-run: would rebuild agents/openai.yaml"

    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip() or "unknown error"
        return False, f"failed to rebuild openai.yaml: {stderr}"
    return True, "rebuilt agents/openai.yaml"


def quick_validate(skill_dir: Path) -> Tuple[bool, str]:
    cmd = ["python3", str(QUICK_VALIDATE), str(skill_dir)]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    output = completed.stdout.strip() or completed.stderr.strip() or "no output"
    return completed.returncode == 0, output


def read_openai_interface(openai_yaml: Path) -> Dict[str, str]:
    text = openai_yaml.read_text(encoding="utf-8")
    match = re.search(r"^interface:\n((?:  .*\n?)*)", text, re.MULTILINE)
    if not match:
        return {}
    return parse_simple_mapping(match.group(1))


def openai_yaml_issues(openai_yaml: Path, skill_name: str) -> List[str]:
    if not openai_yaml.exists():
        return ["missing agents/openai.yaml"]

    interface = read_openai_interface(openai_yaml)
    issues: List[str] = []

    for field in ("display_name", "short_description", "default_prompt"):
        if not interface.get(field):
            issues.append(f"interface.{field} missing")

    default_prompt = interface.get("default_prompt", "")
    if f"${skill_name}" not in default_prompt:
        issues.append("default_prompt does not bind this skill token")

    referenced_tokens = {token for token in re.findall(r"\$(vk-[a-z0-9-]+)", default_prompt)}
    if referenced_tokens and referenced_tokens != {skill_name}:
        issues.append("default_prompt references another skill token")

    return issues


def legacy_path_issues(text: str) -> List[str]:
    issues: List[str] = []
    if re.search(r"(?<!\.)\./vk-[a-z0-9-]+/", text):
        issues.append("still contains legacy ./vk-xxx/ record paths")
    if re.search(r"\^vk-[a-z0-9-]+/\$", text):
        issues.append("still contains per-skill .gitignore rules")
    normalized = text.replace("`", "")
    has_vk_restore = (
        "git restore --staged vk/" in normalized
        or "git restore --staged -- vk/" in normalized
    )
    has_legacy_restore = "'vk-*'" in normalized or '"vk-*"' in normalized or " vk-*" in normalized
    if not has_vk_restore:
        issues.append("missing unified git restore --staged vk/ rule")
    if not has_legacy_restore:
        issues.append("missing legacy vk-* staged-cleanup rule")
    if "shared/vk-core-contract.md" not in text and "../shared/vk-core-contract.md" not in text:
        issues.append("missing shared/vk-core-contract.md reference")
    shared_result_tokens = (
        "shared result contract",
        "shared summary-card/result contract",
        "summary-card/result contract",
    )
    card_tokens = ("summary card", "Summary card", "summary-card")
    if not any(token in text for token in shared_result_tokens) or not any(
        token in text for token in card_tokens
    ):
        issues.append("missing shared result contract + summary card constraint")
    return issues


def process_skill(skill_dir: Path, dry_run: bool) -> SkillResult:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return SkillResult(skill_dir, "flagged", "missing SKILL.md")

    try:
        frontmatter = read_frontmatter(skill_md)
    except Exception as exc:
        return SkillResult(skill_dir, "flagged", f"frontmatter parse failed: {exc}")

    fm_name = str(frontmatter.get("name", "")).strip()
    if not fm_name:
        return SkillResult(skill_dir, "flagged", "frontmatter missing name")

    if fm_name != skill_dir.name:
        return SkillResult(
            skill_dir,
            "flagged",
            f"frontmatter.name != directory name: {fm_name} != {skill_dir.name}",
        )

    text = skill_md.read_text(encoding="utf-8")
    path_issues = legacy_path_issues(text)
    if path_issues:
        return SkillResult(skill_dir, "flagged", "; ".join(path_issues))

    openai_yaml = skill_dir / "agents" / "openai.yaml"
    yaml_issues = openai_yaml_issues(openai_yaml, fm_name)
    changed = False
    if yaml_issues:
        ok, msg = generate_openai_yaml(skill_dir, fm_name, dry_run=dry_run)
        if not ok:
            return SkillResult(skill_dir, "flagged", msg)
        changed = True

    valid, msg = quick_validate(skill_dir)
    if not valid:
        return SkillResult(skill_dir, "flagged", f"validation failed: {msg}")

    if changed:
        return SkillResult(skill_dir, "updated", "metadata repaired and validation passed")
    return SkillResult(skill_dir, "no_change", "No update required")


def main() -> int:
    parser = argparse.ArgumentParser(description="Conservative auto-evolution for vk-* skills.")
    parser.add_argument(
        "--roots",
        nargs="+",
        default=[
            str(SOURCE_ROOT),
            str(CODEX_SKILLS_DIR),
            str(Path.home() / ".agents" / "skills"),
        ],
        help="Skill roots to scan.",
    )
    parser.add_argument("--prefix", default="vk-", help="Skill folder prefix filter.")
    parser.add_argument("--dry-run", action="store_true", help="Plan only, do not modify files.")
    args = parser.parse_args()

    if not GEN_OPENAI_YAML.exists() or not QUICK_VALIDATE.exists():
        print("[ERROR] required helper scripts are missing; cannot auto-evolve.")
        return 1

    roots = expand_roots(args.roots)
    skills = discover_skills(roots, args.prefix)

    print("auto-evolve mode:", "dry-run" if args.dry_run else "apply")
    print("scan roots:", ", ".join(str(r) for r in roots))
    print("skills matched:", len(skills))

    updated: List[SkillResult] = []
    no_change: List[SkillResult] = []
    flagged: List[SkillResult] = []

    for skill_dir in skills:
        result = process_skill(skill_dir, dry_run=args.dry_run)
        if result.status == "updated":
            updated.append(result)
        elif result.status == "no_change":
            no_change.append(result)
        else:
            flagged.append(result)

    print("\nUpdated Skills:")
    if updated:
        for item in updated:
            print(f"- {item.path}: {item.reason}")
    else:
        print("- None")

    print("\nUnmodified Skills:")
    if no_change:
        for item in no_change:
            print(f"- {item.path}: {item.reason}")
    else:
        print("- None")

    print("\nFlagged Skills:")
    if flagged:
        for item in flagged:
            print(f"- {item.path}: {item.reason}")
    else:
        print("- None")

    print("\nSummary:")
    print(
        f"updated={len(updated)}, no_change={len(no_change)}, flagged={len(flagged)}"
    )
    return 0 if not flagged else 2


if __name__ == "__main__":
    raise SystemExit(main())
