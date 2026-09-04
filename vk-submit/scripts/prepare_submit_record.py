#!/usr/bin/env python3
"""Prepare a local vk-submit record with git baseline and scope-audit output."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL_ROOT / "assets" / "submit_record_template.md"
MIGRATOR = SKILL_ROOT / "scripts" / "migrate_vk_record_dirs.py"
SCOPE_WRITER = SKILL_ROOT / "scripts" / "write_vkpush_scope_record.py"
ALLOWED_RECORD_KEYS = {
    "- Project path:": "",
    "- Work start:": "",
    "- Record file path:": "",
    "- Dry-run manifest path:": "",
    "- `.gitignore` includes `vk/`:": "",
    "- `.gitignore` includes `vk-*/`:": "",
    "- Before: `git status --short --branch` summary:": "",
}
START = "<!-- git-baseline:start -->"
END = "<!-- git-baseline:end -->"


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), check=False, capture_output=True, text=True)


def git(repo_root: Path, *args: str) -> str:
    completed = run(["git", *args], repo_root)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip() or "git command failed"
        raise RuntimeError(f"{' '.join(args)}: {stderr}")
    return completed.stdout.strip()


def rel_to_repo(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def ensure_record_file(record_file: Path) -> None:
    if record_file.exists():
        return
    record_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TEMPLATE, record_file)


def replace_line(text: str, prefix: str, value: str) -> str:
    lines = text.splitlines()
    replaced = False
    for i, line in enumerate(lines):
        if line.startswith(prefix):
            lines[i] = f"{prefix} {value}".rstrip()
            replaced = True
            break
    if not replaced:
        lines.append(f"{prefix} {value}".rstrip())
    return "\n".join(lines) + "\n"


def render_git_baseline(repo_root: Path) -> str:
    status = git(repo_root, "status", "--short", "--branch")
    diff = git(repo_root, "diff", "--name-only")
    cached = git(repo_root, "diff", "--cached", "--name-only")
    stat = git(repo_root, "diff", "--stat")
    cached_stat = git(repo_root, "diff", "--cached", "--stat")
    parts = [
        "## Git Baseline Snapshot",
        START,
        "```text",
        "[git status --short --branch]",
        status or "<empty>",
        "",
        "[git diff --name-only]",
        diff or "<empty>",
        "",
        "[git diff --cached --name-only]",
        cached or "<empty>",
        "",
        "[git diff --stat]",
        stat or "<empty>",
        "",
        "[git diff --cached --stat]",
        cached_stat or "<empty>",
        "```",
        END,
    ]
    return "\n".join(parts)


def upsert_git_baseline(text: str, block: str) -> str:
    if START in text and END in text:
        start = text.index(START)
        line_start = text.rfind("\n", 0, start)
        start = 0 if line_start == -1 else line_start + 1
        end = text.index(END) + len(END)
        return text[:start].rstrip() + "\n" + block + text[end:]
    return text.rstrip() + "\n\n" + block + "\n"


def is_vank_skill_source(repo_root: Path) -> bool:
    return any(repo_root.glob("vk-*/SKILL.md"))


def ensure_gitignore(repo_root: Path) -> tuple[bool, bool, bool]:
    path = repo_root / ".gitignore"
    if not path.exists():
        path.write_text("", encoding="utf-8")
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    changed = False
    legacy_rule_applicable = not is_vank_skill_source(repo_root)
    rules = ("vk/", "vk-*/") if legacy_rule_applicable else ("vk/",)
    for rule in rules:
        if rule not in lines:
            lines.append(rule)
            changed = True
    if changed:
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    final = path.read_text(encoding="utf-8").splitlines()
    return ("vk/" in final, ("vk-*/" in final or not legacy_rule_applicable), legacy_rule_applicable)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare vk-submit local record and baseline.")
    parser.add_argument("--repo-root", default=".", help="Git repo root or any path inside it.")
    parser.add_argument("--record-file", help="Target record file. Defaults to ./vk/submit/submit-record_YYYYMMDD_HHMMSS.md")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    try:
        repo_root = Path(git(repo_root, "rev-parse", "--show-toplevel"))
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1

    if not TEMPLATE.exists() or not MIGRATOR.exists() or not SCOPE_WRITER.exists():
        print("[ERROR] required helper scripts or template missing.")
        return 1

    run(["python3", str(MIGRATOR), "--repo-root", str(repo_root)], repo_root)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    record_file = Path(args.record_file).resolve() if args.record_file else repo_root / "vk" / "submit" / f"submit-record_{ts}.md"
    ensure_record_file(record_file)

    run(["python3", str(SCOPE_WRITER), "--repo-root", str(repo_root), "--record-file", str(record_file)], repo_root)

    vk_ok, legacy_ok, legacy_rule_applicable = ensure_gitignore(repo_root)

    text = record_file.read_text(encoding="utf-8")
    text = replace_line(text, "- Project path:", str(repo_root))
    text = replace_line(text, "- Work start:", datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z").strip())
    text = replace_line(text, "- Record file path:", rel_to_repo(record_file, repo_root))
    text = replace_line(text, "- Dry-run manifest path:", "")
    text = replace_line(text, "- `.gitignore` includes `vk/`:", "yes" if vk_ok else "no")
    legacy_value = "yes" if legacy_ok else "no"
    if not legacy_rule_applicable:
        legacy_value = "not applicable — Vank package source"
    text = replace_line(text, "- `.gitignore` includes `vk-*/`:", legacy_value)
    text = replace_line(text, "- Before: `git status --short --branch` summary:", "see Git Baseline Snapshot below")
    text = upsert_git_baseline(text, render_git_baseline(repo_root))
    record_file.write_text(text, encoding="utf-8")

    print(f"repo_root={repo_root}")
    print(f"record_file={record_file}")
    print("[OK] submit record prepared with git baseline and scope check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
