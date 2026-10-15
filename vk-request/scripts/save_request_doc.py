#!/usr/bin/env python3
"""Create or revise one canonical local request DSL, with durable history."""
from __future__ import annotations

import argparse
import difflib
import fcntl
import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from validate_request_doc import HISTORY_END, HISTORY_START, validate_text

DEFAULT_TEMPLATE_VERSION = "MULTI-AGENT CODING ORCHESTRATION TEMPLATE V3-FINAL"
STATUSES = (
    "awaiting_confirmation", "ready", "in_progress",
    "completed_pending_acceptance", "accepted", "blocked", "deferred", "cancelled",
)


def slugify(value: str) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "-", value.strip().lower()).strip("-") or "untitled"


def read_document(text: str) -> tuple[dict[str, str], str, str]:
    """Keep raw YAML blocks so unrelated metadata is preserved without PyYAML."""
    fields: dict[str, str] = {}
    if text.startswith("---\n"):
        parts = text[4:].split("\n---\n", 1)
        if len(parts) != 2:
            raise ValueError("unclosed frontmatter; refusing to replace it")
        header, text = parts
        key = ""
        for line in header.splitlines():
            match = re.match(r"^([A-Za-z_][\w-]*):", line)
            if match:
                key = match[1]
                if key in fields:
                    raise ValueError(f"duplicate metadata field: {key}")
                fields[key] = line + "\n"
            elif key:
                fields[key] += line + "\n"
            else:
                raise ValueError("unsupported frontmatter; update this document in its native format")
    history = ""
    if HISTORY_START in text or HISTORY_END in text:
        if text.count(HISTORY_START) != 1 or text.count(HISTORY_END) != 1:
            raise ValueError("malformed history markers")
        text, tail = text.split(HISTORY_START, 1)
        if HISTORY_END not in tail:
            raise ValueError("unclosed history")
        history, trailing = tail.split(HISTORY_END, 1)
        if trailing.strip():
            raise ValueError("content after managed history; refusing to discard it")
        history = history.strip()
    return fields, text.strip(), history


def scalar(fields: dict[str, str], key: str, default: str = "") -> str:
    if key not in fields:
        return default
    value = fields[key].split(":", 1)[1].strip()
    if value.startswith('"'):
        try:
            return str(json.loads(value))
        except ValueError as exc:
            raise ValueError(f"unsupported quoted {key}; preserve/edit it in its native format") from exc
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if "\n" in value or value.startswith(("|", ">")):
        raise ValueError(f"{key} must be a scalar")
    return value.split(" #", 1)[0].strip()


def set_field(fields: dict[str, str], key: str, value: str | int) -> None:
    fields[key] = f"{key}: {json.dumps(value, ensure_ascii=False)}\n"


def original_request(fields: dict[str, str]) -> str:
    raw = fields.get("source_request", "").splitlines()
    if raw and raw[0].split(":", 1)[1].strip() in ("|", "|-", "|+"):
        return "\n".join(line[2:] if line.startswith("  ") else line for line in raw[1:]).rstrip()
    return scalar(fields, "source_request")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--path", help="Existing canonical DSL path, relative to repo root or absolute.")
    parser.add_argument("--task-id", help="Stable matter ID, e.g. REQ-001; resolves an existing file first.")
    parser.add_argument("--new", action="store_true", help="Explicitly create an independent same-title matter.")
    parser.add_argument("--title")
    parser.add_argument("--source-request", help="Original request on creation; subsequent requests enter history.")
    parser.add_argument("--template-version")
    parser.add_argument("--status", choices=STATUSES)
    parser.add_argument("--iteration")
    parser.add_argument("--iteration-summary", help="New iteration goal, scope delta, criteria, and relationship.")
    parser.add_argument("--change-summary", help="Reason and concrete changes; required for an update.")
    parser.add_argument("--evidence", help="Verification result and code/worktree baseline.")
    parser.add_argument("--acceptance-evidence", help="User/agreed mechanism, accepted scope, time, and result.")
    parser.add_argument("--expected-revision", type=int, help="Required for existing files; reject stale updates (legacy files start at 1).")
    return parser.parse_args()


def resolve_path(args: argparse.Namespace, directory: Path) -> tuple[Path, str]:
    if args.new and args.path:
        raise ValueError("--new cannot be combined with --path")
    if args.task_id and not re.fullmatch(r"REQ-[0-9]{3,}", args.task_id):
        raise ValueError("--task-id must be REQ- followed by at least three digits")
    records = []
    for path in sorted(directory.glob("*.md")):
        fields, _, _ = read_document(path.read_text(encoding="utf-8"))
        records.append((path, scalar(fields, "task_id"), scalar(fields, "title", path.stem)))
    ids = [task_id for _, task_id, _ in records if task_id]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate task IDs; resolve canonical documents before saving")
    if args.path:
        path = Path(args.path)
        path = (Path(args.repo_root).resolve() / path).resolve() if not path.is_absolute() else path.resolve()
        if path.parent != directory or path.suffix != ".md" or not path.is_file():
            raise ValueError("--path must be an existing .md file directly under vk/request/")
        existing_id = scalar(read_document(path.read_text(encoding="utf-8"))[0], "task_id")
        if args.task_id and existing_id and args.task_id != existing_id:
            raise ValueError("--task-id conflicts with the existing document")
        if args.task_id in ids and not existing_id:
            raise ValueError("--task-id already belongs to another document")
    else:
        matches = [path for path, task_id, _ in records if args.task_id and task_id == args.task_id]
        if matches:
            if args.new:
                raise ValueError("--new cannot reuse an existing task ID")
            return matches[0], args.task_id
        same_title = [path for path, _, title in records if args.title and slugify(title) == slugify(args.title)]
        if same_title and not args.new:
            raise ValueError("same-title candidate(s); resolve with --path/--task-id, or --new for an independent matter: "
                             + ", ".join(str(path) for path in same_title))
        if not args.title or not args.title.strip():
            raise ValueError("--title is required for a new matter")
        path = None
        existing_id = ""
    next_number = max([int(task_id[4:]) for task_id in ids if re.fullmatch(r"REQ-[0-9]+", task_id)] or [0]) + 1
    task_id = existing_id or args.task_id or f"REQ-{next_number:03d}"
    return path or directory / f"{task_id}-{slugify(args.title)}.md", task_id


def fenced(text: str, language: str = "") -> str:
    size = max([len(run) + 1 for run in re.findall(r"`+", text)] + [3])
    fence = "`" * size
    return f"{fence}{language}\n{text.rstrip()}\n{fence}"


def save(args: argparse.Namespace, content: str, directory: Path) -> Path:
    path, task_id = resolve_path(args, directory)
    original = path.read_text(encoding="utf-8") if path.exists() else None
    fields, old_body, history = read_document(original or "")
    previous = fields.copy()
    old_revision = int(scalar(fields, "revision", "1")) if original is not None else 0
    if old_revision < 0 or (original is not None and old_revision == 0):
        raise ValueError("revision must be a positive integer")
    if original is not None and args.expected_revision is None:
        raise ValueError("existing documents require --expected-revision from the last read (legacy: 1)")
    if args.expected_revision is not None and args.expected_revision != old_revision:
        raise ValueError(f"stale revision: expected {args.expected_revision}, current {old_revision}")
    old_status = scalar(fields, "status", "awaiting_confirmation")
    old_iteration = scalar(fields, "iteration", "I01")
    iteration = args.iteration or old_iteration
    if not re.fullmatch(r"I[0-9]{2,}", iteration) or int(iteration[1:]) == 0:
        raise ValueError("iteration must be I followed by a positive number, e.g. I01")
    new_iteration = iteration != old_iteration
    if new_iteration and not (args.iteration_summary and args.iteration_summary.strip()):
        raise ValueError("iteration changes require --iteration-summary")
    status = args.status or ("awaiting_confirmation" if new_iteration else old_status)
    if status not in STATUSES:
        raise ValueError("legacy status is unknown; supply --status after inspecting the document")
    if original is not None and old_status == "accepted" and content != old_body and not args.status and not new_iteration:
        raise ValueError("accepted content changed; explicitly reopen affected scope with --status or record fresh acceptance")
    entering_completion = status == "completed_pending_acceptance" and (old_status != status or new_iteration or content != old_body)
    if entering_completion and not (args.evidence and args.evidence.strip()):
        raise ValueError("completion requires --evidence with passing required checks and baseline")
    accepting = status == "accepted" and (original is None or old_status != status or new_iteration or content != old_body)
    if accepting and not (args.acceptance_evidence and args.acceptance_evidence.strip()):
        raise ValueError("acceptance requires --acceptance-evidence; tests/push alone are not acceptance")
    set_field(fields, "task_id", task_id)
    set_field(fields, "title", args.title if args.title is not None else scalar(fields, "title", path.stem))
    set_field(fields, "iteration", iteration)
    set_field(fields, "status", status)
    set_field(fields, "template_version", args.template_version or scalar(fields, "template_version", DEFAULT_TEMPLATE_VERSION))
    if "source_request" not in fields:
        set_field(fields, "source_request", args.source_request or "")
    elif args.source_request and args.source_request != original_request(fields):
        set_field(fields, "last_change_request", args.source_request)
    if args.iteration_summary:
        set_field(fields, "iteration_summary", args.iteration_summary)
    if args.evidence:
        set_field(fields, "last_verification", args.evidence)
    if args.acceptance_evidence:
        set_field(fields, "last_acceptance", args.acceptance_evidence)
    changed = {key: (previous.get(key, ""), value) for key, value in fields.items() if previous.get(key) != value}
    if original is not None and not changed and content == old_body:
        return path
    if original is not None and not (args.change_summary and args.change_summary.strip()):
        raise ValueError("updates require --change-summary describing the reason and concrete changes")
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    revision = old_revision + 1
    if "created_at" not in fields:
        created = datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(timespec="seconds") if original is not None else now
        set_field(fields, "created_at", created)
    set_field(fields, "updated_at", now)
    set_field(fields, "revision", revision)
    entry = f"### r{revision} — {iteration} — {now}\n\n"
    entry += (args.change_summary or "Created canonical requirement document.") + "\n"
    entry += f"\nStatus: {old_status if original is not None else 'new'} -> {status}\n"
    if args.source_request and original is not None:
        entry += "\nChange request:\n\n" + fenced(args.source_request) + "\n"
    if args.iteration_summary:
        entry += "\nIteration: " + args.iteration_summary + "\n"
    for label, evidence in (("Verification", args.evidence), ("Acceptance", args.acceptance_evidence)):
        if evidence:
            entry += f"\n{label}: {evidence}\n"
    if original is not None:
        before = "".join(previous.values()) + "\n" + old_body + "\n"
        after = "".join(fields.values()) + "\n" + content + "\n"
        delta = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                             fromfile=f"r{old_revision}", tofile=f"r{revision}"))
        entry += "\nChanges (previous metadata/body -> current):\n\n" + fenced(delta, "diff") + "\n"
    history = (history + "\n\n" + entry).strip()
    rendered = "---\n" + "".join(fields.values()) + "---\n\n" + content + "\n\n" + HISTORY_START + "\n" + history + "\n" + HISTORY_END + "\n"
    read_document(rendered)  # Reject input that would corrupt the history envelope.
    failures, _ = validate_text(rendered)
    if failures:
        raise ValueError("invalid current DSL: " + "; ".join(failures))
    fd, temporary = tempfile.mkstemp(prefix=".request-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(rendered)
            stream.flush()
            os.fsync(stream.fileno())
        if (path.read_text(encoding="utf-8") if path.exists() else None) != original:
            raise ValueError("document changed while saving; read it again before retrying")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return path


def main() -> int:
    args = parse_args()
    content = sys.stdin.read().strip()
    failures, _ = validate_text(content)
    if not content or content.startswith("---\n") or HISTORY_START in content or HISTORY_END in content:
        print("error: stdin must contain only the current DSL body, without frontmatter/history", file=sys.stderr)
        return 1
    if failures:
        print("error: invalid DSL: " + "; ".join(failures), file=sys.stderr)
        return 1
    try:
        repo_root = Path(args.repo_root).resolve()
        directory = (repo_root / "vk" / "request").resolve()
        if not directory.is_relative_to(repo_root):
            raise ValueError("vk/request/ must resolve inside the target repository")
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / ".request-save.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            print(save(args, content, directory))
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
