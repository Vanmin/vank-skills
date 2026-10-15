"""Synthetic purchase-delivery records for workflow behavioral tests."""
from __future__ import annotations

import copy
import json
from datetime import datetime, timedelta

STEPS = ["awaiting_confirmation", "ready", "in_progress", "testing", "completed_pending_acceptance", "accepted", "completed"]


def at(minute):
    return f"2026-10-15T10:{minute:02d}:00+08:00"


def sample(status="awaiting_confirmation"):
    rank = STEPS.index(status)
    data = {
        "schema_version": 1, "task_id": "REQ-001", "iteration": "I01", "status": status,
        "baseline": "build-abc" if rank >= 3 else "", "confirmation": {},
        "features": [{"id": "FEAT-001", "title": "Purchase", "revision": 1, "required": True,
                      "implementation": "implemented" if rank >= 3 else "pending",
                      "implementation_evidence": "Purchase handler implemented in build-abc" if rank >= 3 else "",
                      "criteria": [{"id": "AC-001", "description": "One purchase creates one charge", "required": True}]}],
        "tests": [{"id": "TC-001", "run_id": "plan-1", "criteria": ["AC-001"],
                   "scope_versions": {"FEAT-001": 1}, "required": True, "status": "not_run"}],
        "issues": [], "acceptance": [],
        "events": [{"status": stage, "at": at(i), "evidence": f"Synthetic purchase workflow: {stage}"}
                   for i, stage in enumerate(STEPS[:rank + 1])],
    }
    if rank >= 1:
        data["confirmation"] = {"by": "Product owner", "at": at(1), "evidence": "Approved purchase scope",
                                "scope_versions": {"FEAT-001": 1}}
    if rank >= 4:
        data["tests"].append({"id": "TC-001", "run_id": "run-1", "criteria": ["AC-001"],
                              "scope_versions": {"FEAT-001": 1}, "required": True, "status": "pass",
                              "at": at(3), "baseline": "build-abc", "evidence": "Purchase test output PASS"})
    if rank >= 5:
        data["acceptance"].append({"id": "ACC-001", "criteria": ["AC-001"], "scope_versions": {"FEAT-001": 1},
                                   "status": "pass", "at": at(5), "by": "Product owner", "mechanism": "user",
                                   "baseline": "build-abc", "evidence": "Owner accepted purchase criterion"})
    if rank >= 6:
        data["closure"] = {"by": "Developer", "at": at(6), "evidence": "Requirement/review synced; no required work remains",
                           "documents_synced": True}
    return data


def block(data):
    return "<!-- vk:lifecycle:start -->\n```json\n" + json.dumps(data, indent=2) + "\n```\n<!-- vk:lifecycle:end -->"


def advance(data, status):
    data = copy.deepcopy(data)
    if data["status"] != status:
        moments = [datetime.fromisoformat(event["at"]) for event in data["events"]]
        moments += [datetime.fromisoformat(record["at"]) for record in data["tests"] + data["acceptance"] if "at" in record]
        moments += [datetime.fromisoformat(event["at"]) for issue in data["issues"] for event in issue["history"]]
        moment = (max(moments) + timedelta(minutes=1)).isoformat()
        data["events"].append({"status": status, "at": moment, "evidence": "Explicit synthetic stage transition"})
    data["status"] = status
    if status == "accepted" and not data["acceptance"]:
        record = sample("accepted")["acceptance"][0]
        record["at"] = data["events"][-1]["at"]
        data["acceptance"].append(record)
    return data
