"""End-to-end delivery gates and failure/repair/retest/reacceptance loops."""
from __future__ import annotations

import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
from check_delivery_lifecycle import check_document, extract, validate
from save_request_doc import read_document, scalar
from delivery_fixtures import STEPS, advance, at, block, sample


class DeliveryWorkflowTests(unittest.TestCase):
    def assert_valid(self, data, **kwargs):
        self.assertEqual(validate(data, **kwargs), [])

    def test_every_happy_path_stage_passes_with_realistic_declared_evidence(self):
        previous = None
        for stage in STEPS:
            with self.subTest(stage=stage):
                data = sample(stage)
                self.assert_valid(data, previous=previous)
                previous = data

    def test_full_native_requirement_can_be_saved_through_completion_in_one_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = None
            for revision, stage in enumerate(STEPS, 1):
                command = [sys.executable, str(SKILL / "scripts" / "save_request_doc.py"), "--repo-root", tmp,
                           "--format", "requirement", "--status", stage]
                if path is None:
                    command += ["--title", "Purchase"]
                else:
                    command += ["--path", str(path), "--expected-revision", str(revision - 1),
                                "--change-summary", "Advance purchase workflow to " + stage]
                if stage == "completed_pending_acceptance":
                    command += ["--evidence", "Required purchase tests passed on build-abc"]
                if stage == "accepted":
                    command += ["--acceptance-evidence", "Owner accepted AC-001 on build-abc"]
                result = subprocess.run(command, input="# Purchase requirement\n\n" + block(sample(stage)),
                                        text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                new_path = Path(result.stdout.strip())
                self.assertTrue(path is None or path == new_path)
                path = new_path
                fields, _, history = read_document(path.read_text())
                self.assertEqual(scalar(fields, "status"), stage)
                self.assertEqual(scalar(fields, "revision"), str(revision))
                self.assertEqual(check_document(path.read_text(), status=stage), [])
            self.assertEqual(len(list(path.parent.glob("*.md"))), 1)
            self.assertIn("r1", history)
            self.assertIn("r7", history)
            result = subprocess.run([sys.executable, str(SKILL / "scripts" / "check_delivery_lifecycle.py"),
                                     str(path), "--gate", "completed"], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_confirmation_is_required_before_development(self):
        data = sample("in_progress")
        data["confirmation"] = {}
        self.assertTrue(validate(data))
        data = sample("ready")
        data["confirmation"]["scope_versions"]["FEAT-001"] = 99
        self.assertIn("scope confirmation", " ".join(validate(data)))

    def test_testing_requires_implementation_and_criterion_coverage(self):
        data = sample("testing")
        data["features"][0]["implementation"] = "in_progress"
        data["tests"] = []
        errors = " ".join(validate(data))
        self.assertIn("implementation is incomplete", errors)
        self.assertIn("missing required test coverage", errors)

    def test_unrun_failed_blocked_and_stale_tests_prevent_acceptance_readiness(self):
        for mutation in ("not_run", "fail", "blocked", "old_baseline", "old_scope"):
            with self.subTest(mutation=mutation):
                data = sample("completed_pending_acceptance")
                if mutation == "old_baseline":
                    data["tests"][-1]["baseline"] = "old-build"
                elif mutation == "old_scope":
                    data["tests"][-1]["scope_versions"]["FEAT-001"] = 2
                else:
                    data["tests"][-1]["status"] = mutation
                    if mutation in ("fail", "blocked"):
                        data["issues"] = [self.issue()]
                        data["tests"][-1]["issue_id"] = "F-001"
                self.assertTrue(validate(data))

    def issue(self, status="open"):
        return {"id": "F-001", "criteria": ["AC-001"], "source": "acceptance", "blocking": True,
                "status": status, "history": [{"status": status, "at": at(6), "evidence": "Duplicate charge observed"}]}

    def repaired(self):
        old = sample("accepted")
        data = advance(old, "in_progress")
        issue = self.issue()
        issue["status"] = "verified_resolved"
        issue["history"] += [
            {"status": "fixed_pending_verification", "at": at(7), "evidence": "Idempotency repaired"},
            {"status": "verified_resolved", "at": at(9), "evidence": "Repair retest passed"},
        ]
        issue["resolution"] = {"kind": "repair", "at": at(7), "baseline": "build-fixed",
                               "scope_versions": {"FEAT-001": 1}, "evidence": "Fix duplicate charge"}
        issue["retest_runs"] = ["repair-run"]
        data["issues"] = [issue]
        data["baseline"] = "build-fixed"
        test = copy.deepcopy(data["tests"][-1])
        test.update(run_id="repair-run", baseline="build-fixed", at=at(8), evidence="Duplicate submit and normal purchase PASS")
        data["tests"].append(test)
        return old, data

    def test_acceptance_failure_repair_retest_reacceptance_retains_prior_attempts(self):
        old, repaired = self.repaired()
        failed = copy.deepcopy(old["acceptance"][-1])
        failed.update(id="ACC-fail", status="fail", at=at(6), issue_id="F-001", evidence="Owner found duplicate charge")
        repaired["acceptance"].append(failed)
        self.assert_valid(repaired, previous=old)
        ready = advance(repaired, "completed_pending_acceptance")
        self.assert_valid(ready)
        accepted = advance(ready, "accepted")
        self.assertIn("has not passed acceptance", " ".join(validate(accepted)))
        retry = copy.deepcopy(old["acceptance"][-1])
        retry.update(id="ACC-retry", at=at(10), baseline="build-fixed", evidence="Owner reaccepted fixed purchase")
        accepted["acceptance"].append(retry)
        self.assert_valid(accepted)
        self.assertEqual(len(accepted["acceptance"]), 3)
        self.assertEqual(accepted["issues"][0]["id"], "F-001")

    def test_code_fix_without_retest_cannot_close_issue(self):
        _, data = self.repaired()
        data["tests"][-1]["at"] = at(6)
        self.assertIn("passing retests after", " ".join(validate(data)))
        _, data = self.repaired()
        data["issues"][0]["retest_runs"] = []
        self.assertIn("all affected criteria", " ".join(validate(data)))

    def test_earlier_acceptance_does_not_cover_a_later_repair(self):
        _, data = self.repaired()
        data = advance(data, "accepted")
        self.assertIn("acceptance predates issue", " ".join(validate(data)))

    def test_historical_retest_is_not_erased_or_rebound_to_a_new_run(self):
        _, data = self.repaired()
        data["baseline"] = "later-build"
        latest = copy.deepcopy(data["tests"][-1])
        latest.update(run_id="later-failure", baseline="later-build", at=at(12), status="fail", issue_id="F-001")
        data["tests"].append(latest)
        data["issues"][0]["status"] = "reopened"
        data["issues"][0]["history"].append({"status": "reopened", "at": at(12), "evidence": "Same failure returned on later build"})
        self.assert_valid(data)  # Historical repair remains historical; current in_progress records the new failure.
        self.assertTrue(validate(data, gate="completed_pending_acceptance"))

    def test_partial_acceptance_does_not_accept_the_whole_requirement(self):
        data = sample("accepted")
        criterion = {"id": "AC-002", "description": "Order appears in history", "required": True}
        data["features"][0]["criteria"].append(criterion)
        data["tests"][-1]["criteria"].append("AC-002")
        self.assertIn("AC-002: current scope has not passed acceptance", validate(data))

    def test_completion_requires_acceptance_and_document_closure(self):
        data = sample("completed")
        data["acceptance"] = []
        data["closure"]["documents_synced"] = False
        errors = " ".join(validate(data))
        self.assertIn("has not passed acceptance", errors)
        self.assertIn("synchronization/closure", errors)

    def test_scope_change_invalidates_affected_evidence_and_requires_confirmation(self):
        old = sample("accepted")
        data = copy.deepcopy(old)
        data["features"][0]["criteria"][0]["description"] = "Batch purchase charges once"
        self.assertIn("scope revision", " ".join(validate(data, previous=old)))
        data["features"][0]["revision"] = 2
        self.assertIn("scope confirmation", " ".join(validate(data, previous=old)))
        data["confirmation"]["scope_versions"]["FEAT-001"] = 2
        errors = " ".join(validate(data, previous=old))
        self.assertIn("stale", errors)
        self.assertIn("has not passed acceptance", errors)

    def test_history_and_problem_identity_cannot_be_deleted(self):
        old, data = self.repaired()
        data["acceptance"] = []
        self.assertIn("append-only", " ".join(validate(data, previous=old)))
        old = self.repaired()[1]
        data = copy.deepcopy(old)
        data["issues"] = []
        self.assertIn("preserve issue IDs", " ".join(validate(data, previous=old)))

    def test_failed_results_require_a_linked_problem(self):
        data = sample("testing")
        data["tests"][0].update(status="fail", at=at(3), baseline="build-abc", evidence="Duplicate charge")
        self.assertIn("must link a recorded issue", " ".join(validate(data)))

    def test_any_phase_problem_is_recorded_and_blocks_forward_acceptance(self):
        for source, stage in (("requirements", "awaiting_confirmation"), ("development", "in_progress"),
                              ("review", "in_progress"), ("testing", "testing"), ("acceptance", "completed_pending_acceptance")):
            with self.subTest(source=source):
                data = sample(stage)
                issue = self.issue()
                issue["source"] = source
                data["issues"] = [issue]
                if stage != "completed_pending_acceptance":
                    self.assert_valid(data)
                self.assertTrue(validate(data, gate="completed_pending_acceptance"))
                ready = sample("completed_pending_acceptance")
                ready["issues"] = [issue]
                self.assertIn("unresolved blocking issue", " ".join(validate(ready)))

    def test_agreed_acceptance_requires_the_actual_prior_agreement(self):
        data = sample("accepted")
        data["acceptance"][0]["mechanism"] = "agreed"
        self.assertIn("prior agreement", " ".join(validate(data)))
        data["acceptance"][0]["agreement"] = "Owner explicitly authorized this purchase scenario to accept automatically after its specified tests"
        self.assert_valid(data)

    def test_stage_skipping_and_metadata_disagreement_are_rejected(self):
        self.assertIn("cannot skip stages", " ".join(validate(sample("accepted"), previous=sample("in_progress"))))
        self.assertIn("cannot skip stages", " ".join(validate(sample("testing"), previous=sample("ready"))))
        text = block(sample("testing"))
        self.assertIn("document status disagrees", " ".join(check_document(text, status="accepted")))

    def test_regression_requires_reopening_the_same_issue(self):
        _, data = self.repaired()
        latest = copy.deepcopy(data["tests"][-1])
        latest.update(run_id="regression", status="fail", at=at(12), issue_id="F-001")
        data["tests"].append(latest)
        self.assertIn("reopening the same issue", " ".join(validate(data)))

    def test_early_closure_and_acceptance_before_testing_are_rejected(self):
        data = sample("completed")
        data["closure"]["at"] = at(1)
        self.assertIn("closure must follow", " ".join(validate(data)))
        data = sample("accepted")
        data["acceptance"][0]["at"] = at(2)
        self.assertIn("acceptance must follow passing tests", " ".join(validate(data)))

    def test_unaffected_acceptance_survives_repair_of_another_feature(self):
        _, data = self.repaired()
        feature = {"id": "FEAT-002", "title": "Order history", "revision": 1, "required": True,
                   "implementation": "implemented", "implementation_evidence": "History handler unchanged",
                   "criteria": [{"id": "AC-002", "description": "Read order history", "required": True}]}
        data["features"].append(feature)
        data["confirmation"]["scope_versions"]["FEAT-002"] = 1
        historic = {"id": "TC-002", "run_id": "history-old", "criteria": ["AC-002"],
                    "scope_versions": {"FEAT-002": 1}, "required": True, "status": "pass",
                    "at": at(3), "baseline": "build-abc", "evidence": "Order history passed"}
        fresh = dict(historic, run_id="history-current", at=at(9), baseline="build-fixed", evidence="Unchanged history regression passed")
        data["tests"] += [historic, fresh]
        unaffected = {"id": "ACC-history", "criteria": ["AC-002"], "scope_versions": {"FEAT-002": 1},
                      "status": "pass", "at": at(5), "baseline": "build-abc", "by": "Owner", "mechanism": "user",
                      "evidence": "Owner accepted history before purchase repair"}
        data["acceptance"].append(unaffected)
        data = advance(data, "completed_pending_acceptance")
        data = advance(data, "accepted")
        retry = dict(sample("accepted")["acceptance"][0], id="ACC-purchase-retry", at=at(10), baseline="build-fixed")
        data["acceptance"].append(retry)
        self.assert_valid(data)
        self.assertEqual(data["acceptance"][1], unaffected)

    def test_native_save_rejects_stage_skip_without_changing_canonical_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = [sys.executable, str(SKILL / "scripts" / "save_request_doc.py"), "--repo-root", tmp, "--format", "requirement"]
            created = subprocess.run(base + ["--title", "Purchase", "--status", "ready"],
                                     input=block(sample("ready")), text=True, capture_output=True)
            self.assertEqual(created.returncode, 0, created.stderr)
            path = Path(created.stdout.strip())
            original = path.read_bytes()
            rejected = subprocess.run(base + ["--path", str(path), "--expected-revision", "1", "--status", "testing",
                                              "--change-summary", "Attempt to skip development"],
                                      input=block(sample("testing")), text=True, capture_output=True)
            self.assertEqual(rejected.returncode, 1)
            self.assertIn("cannot skip stages", rejected.stderr)
            self.assertEqual(path.read_bytes(), original)

    def test_evidence_string_alone_cannot_claim_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, str(SKILL / "scripts" / "save_request_doc.py"),
                                     "--repo-root", tmp, "--format", "requirement", "--title", "Purchase",
                                     "--status", "accepted", "--acceptance-evidence", "Tests passed"],
                                    input="# Purchase without criterion-linked tests/acceptance", text=True, capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("requires a lifecycle ledger", result.stderr)
            self.assertFalse(list(Path(tmp).rglob("*.md")))

    def test_missing_malformed_or_historical_ledger_cannot_pass(self):
        self.assertTrue(check_document("# No ledger"))
        self.assertTrue(check_document("<!-- vk:lifecycle:start -->{}<!-- vk:lifecycle:end -->"))
        self.assertTrue(check_document("# Current\n<!-- vk:history:start -->\n" + block(sample("completed"))))


if __name__ == "__main__":
    unittest.main()
