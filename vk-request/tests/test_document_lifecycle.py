"""Behavioral regression tests for durable request creation/update safety."""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
from save_request_doc import read_document, scalar
from validate_request_doc import HISTORY_START, validate_text
from check_delivery_lifecycle import extract
from delivery_fixtures import advance, block, sample

TEMPLATE = (SKILL / "references" / "prompt-dsl-template.md").read_text(encoding="utf-8")
BODY = re.sub(r"<<[^>\n]+>>", "TBD", TEMPLATE).strip()


class DocumentLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def invoke(self, *args, body=BODY, ok=True):
        # Supply truthful synthetic workflow evidence for tests whose focus
        # is persistence rather than the separate delivery-gate regressions.
        existing = None
        if "--path" in args:
            existing = Path(args[args.index("--path") + 1])
        elif "--task-id" in args:
            candidates = list((self.root / "vk" / "request").glob(args[args.index("--task-id") + 1] + "-*.md"))
            existing = candidates[0] if len(candidates) == 1 else None
        previous = extract(existing.read_text()) if existing and existing.is_file() else None
        target = args[args.index("--status") + 1] if "--status" in args else (previous["status"] if previous else "awaiting_confirmation")
        iteration = args[args.index("--iteration") + 1] if "--iteration" in args else None
        if iteration and previous and iteration != previous["iteration"] and "--status" not in args:
            target = "awaiting_confirmation"
        if not body.startswith("---\n") and extract(body) is None:
            data = advance(previous, target) if previous else (sample(target) if target != "awaiting_confirmation" else None)
            if data:
                if iteration:
                    data["iteration"] = iteration
                body += "\n\n" + block(data)
        result = subprocess.run(
            [sys.executable, str(SKILL / "scripts" / "save_request_doc.py"),
             "--repo-root", str(self.root), *args],
            input=body, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0 if ok else 1, result.stdout + result.stderr)
        return Path(result.stdout.strip()) if ok else result.stderr

    def create(self, **kwargs):
        return self.invoke("--title", "Order purchase", "--source-request", "Buy one item", **kwargs)

    def update(self, path, revision, *args, **kwargs):
        return self.invoke("--path", str(path), "--expected-revision", str(revision), *args, **kwargs)

    def metadata(self, path):
        return read_document(path.read_text(encoding="utf-8"))[0]

    def test_update_retains_identity_path_creation_and_history(self):
        path = self.create()
        before = self.metadata(path)
        original_history = read_document(path.read_text())[2]
        new_body = BODY.replace("Primary Goal:\nTBD", "Primary Goal:\nBuy several items")
        result = self.update(path, 1, "--title", "Batch purchase", "--change-summary", "Allow batch purchase",
                             "--source-request", "Support several items", "--status", "in_progress", body=new_body)
        fields, body, history = read_document(result.read_text())
        self.assertEqual(result, path)
        self.assertEqual(scalar(fields, "task_id"), scalar(before, "task_id"))
        self.assertEqual(fields["created_at"], before["created_at"])
        self.assertEqual(scalar(fields, "revision"), "2")
        self.assertEqual(scalar(fields, "iteration"), "I01")
        self.assertEqual(scalar(fields, "source_request"), "Buy one item")
        self.assertEqual(body.split("\n<!-- vk:lifecycle:start -->", 1)[0].strip(), new_body)
        self.assertIn(original_history, history)
        self.assertIn("-TBD", history)
        self.assertIn("+Buy several items", history)
        self.assertIn("Support several items", history)
        self.assertEqual(len(list(path.parent.glob("*.md"))), 1)

    def test_unchanged_save_is_byte_identical(self):
        path = self.create()
        before, modified = path.read_bytes(), path.stat().st_mtime_ns
        self.update(path, 1)
        self.update(path, 1, "--source-request", "Buy one item")
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(path.stat().st_mtime_ns, modified)

    def test_same_title_needs_resolution_and_new_is_explicit(self):
        path = self.create()
        self.assertIn("same-title", self.create(ok=False))
        second = self.invoke("--title", "Order purchase", "--new")
        self.assertNotEqual(second, path)
        self.assertNotEqual(scalar(self.metadata(second), "task_id"), scalar(self.metadata(path), "task_id"))
        self.assertIn("same-title", self.create(ok=False))
        self.invoke("--task-id", "REQ-001", "--expected-revision", "1")

    def test_stale_or_missing_revision_cannot_overwrite(self):
        path = self.create()
        self.update(path, 1, "--status", "in_progress", "--change-summary", "Start implementation")
        before = path.read_bytes()
        self.assertIn("stale revision", self.update(path, 1, "--status", "ready", ok=False))
        self.assertIn("expected-revision", self.invoke("--path", str(path), ok=False))
        self.assertEqual(path.read_bytes(), before)

    def test_completion_and_acceptance_require_separate_evidence(self):
        path = self.create()
        before = path.read_bytes()
        self.assertIn("completion requires", self.update(path, 1, "--status", "completed_pending_acceptance", ok=False))
        self.assertEqual(path.read_bytes(), before)
        self.update(path, 1, "--status", "completed_pending_acceptance", "--change-summary", "Implementation verified",
                    "--evidence", "Functional checks PASS at commit abc, clean tree")
        self.assertEqual(scalar(self.metadata(path), "status"), "completed_pending_acceptance")
        self.assertIn("acceptance requires", self.update(path, 2, "--status", "accepted", ok=False))
        self.update(path, 2, "--status", "accepted", "--change-summary", "User accepted purchase flow",
                    "--acceptance-evidence", "User accepted all I01 criteria on 2026-10-15")
        self.assertEqual(scalar(self.metadata(path), "status"), "accepted")

    def test_changed_accepted_scope_must_reopen_or_reaccept(self):
        path = self.invoke("--title", "Order purchase", "--status", "accepted", "--acceptance-evidence", "User accepted I01")
        changed = BODY + "\nNew scope: batch purchase"
        before = path.read_bytes()
        self.assertIn("accepted content changed", self.update(path, 1, "--change-summary", "Add batch", body=changed, ok=False))
        self.assertIn("acceptance requires", self.update(path, 1, "--status", "accepted", body=changed, ok=False))
        self.assertEqual(path.read_bytes(), before)
        self.update(path, 1, "--status", "in_progress", "--change-summary", "Reopen affected purchase scope", body=changed)
        self.assertEqual(scalar(self.metadata(path), "status"), "in_progress")
        self.assertIn("User accepted I01", read_document(path.read_text())[2])

    def test_iteration_stays_in_same_document_and_preserves_acceptance(self):
        path = self.invoke("--title", "Order purchase", "--status", "accepted", "--acceptance-evidence", "User accepted I01")
        self.assertIn("iteration-summary", self.update(path, 1, "--iteration", "I02", ok=False))
        self.update(path, 1, "--iteration", "I02", "--iteration-summary", "Add coupons; I01 purchase remains accepted; coupon criteria TBD",
                    "--change-summary", "Begin coupon delivery iteration")
        fields, _, history = read_document(path.read_text())
        self.assertEqual(scalar(fields, "iteration"), "I02")
        self.assertEqual(scalar(fields, "status"), "awaiting_confirmation")
        self.assertIn("User accepted I01", history)
        self.assertEqual(len(list(path.parent.glob("*.md"))), 1)

    def test_legacy_file_adoption_preserves_metadata_and_old_text(self):
        directory = self.root / "vk" / "request"
        directory.mkdir(parents=True)
        path = directory / "request-20260101-010000-order.md"
        path.write_text('---\ntitle: "Order purchase"\ncreated_at: "2026-01-01"\nsource_request: |-\n  Original request\nowner: "Alice"\nrelated:\n  - review.md\n---\n\n' + BODY)
        self.update(path, 1, "--change-summary", "Adopt existing requirement", body=BODY + "\nCurrent feature status: ready")
        fields, _, history = read_document(path.read_text())
        self.assertEqual(scalar(fields, "created_at"), "2026-01-01")
        self.assertEqual(scalar(fields, "owner"), "Alice")
        self.assertEqual(fields["related"], "related:\n  - review.md\n")
        self.assertIn("Original request", fields["source_request"])
        self.assertEqual(scalar(fields, "revision"), "2")
        self.assertIn("Current feature status", history)

    def test_bad_input_cannot_replace_valid_file(self):
        path = self.create()
        before = path.read_bytes()
        self.update(path, 1, "--change-summary", "Broken input", body="not a DSL", ok=False)
        self.update(path, 1, "--change-summary", "Unresolved input", body=BODY + "\n<<UNRESOLVED>>", ok=False)
        self.update(path, 1, "--change-summary", "Entire old file", body=path.read_text(), ok=False)
        self.assertEqual(path.read_bytes(), before)

    def test_history_cannot_supply_missing_current_chapters_or_fail_old_placeholders(self):
        self.assertTrue(validate_text("SYSTEM:\nEND TEMPLATE\n" + HISTORY_START + "\n" + BODY)[0])
        self.assertFalse(validate_text(BODY + "\n" + HISTORY_START + "\n<<OLD_PLACEHOLDER>>")[0])

    def test_corrupt_history_or_trailing_text_is_not_discarded(self):
        path = self.create()
        path.write_text(path.read_text() + "\nImportant trailing note\n")
        before = path.read_bytes()
        self.assertIn("after managed history", self.update(path, 1, "--change-summary", "Try update", ok=False))
        self.assertEqual(path.read_bytes(), before)

    def test_history_delimiters_in_change_reason_cannot_corrupt_a_file(self):
        path = self.create()
        before = path.read_bytes()
        self.update(path, 1, "--status", "in_progress", "--change-summary", HISTORY_START, ok=False)
        self.assertEqual(path.read_bytes(), before)

    def test_two_writers_from_same_revision_cannot_lose_an_update(self):
        path = self.create()
        def write(status):
            return subprocess.run(
                [sys.executable, str(SKILL / "scripts" / "save_request_doc.py"),
                 "--repo-root", str(self.root), "--path", str(path), "--expected-revision", "1",
                 "--status", status, "--change-summary", f"Set {status}"],
                input=BODY + "\n\n" + block(sample(status)), text=True, capture_output=True,
            )
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(write, ("in_progress", "ready")))
        self.assertEqual(sorted(result.returncode for result in results), [0, 1])
        self.assertIn("stale revision", next(result.stderr for result in results if result.returncode))
        self.assertEqual(scalar(self.metadata(path), "revision"), "2")

    def test_path_and_id_conflicts_fail_without_changes(self):
        path = self.create()
        self.assertIn("conflicts", self.update(path, 1, "--task-id", "REQ-999", ok=False))
        outside = self.root / "outside.md"
        outside.write_text(BODY)
        self.assertIn("under vk/request", self.update(outside, 1, ok=False))
        self.assertEqual(outside.read_text(), BODY)
        self.assertEqual(scalar(self.metadata(path), "revision"), "1")

    def test_update_without_change_reason_is_rejected(self):
        path = self.create()
        before = path.read_bytes()
        self.assertIn("change-summary", self.update(path, 1, "--status", "in_progress", ok=False))
        self.assertEqual(path.read_bytes(), before)

    def test_change_request_only_is_a_recorded_revision(self):
        path = self.create()
        self.update(path, 1, "--source-request", "Clarify existing criteria; no behavior change", "--change-summary", "Record clarification")
        self.assertEqual(scalar(self.metadata(path), "revision"), "2")
        self.assertIn("Clarify existing criteria", read_document(path.read_text())[2])

    def test_parallel_creations_do_not_collide(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            paths = list(pool.map(lambda n: self.invoke("--title", f"Independent requirement {n}"), range(4)))
        self.assertEqual(len(set(paths)), 4)
        self.assertEqual(len({scalar(self.metadata(path), "task_id") for path in paths}), 4)
        self.assertEqual(len(list(paths[0].parent.glob("*.md"))), 4)


if __name__ == "__main__":
    unittest.main()
