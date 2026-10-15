#!/usr/bin/env python3
"""Check requirement -> development -> testing -> acceptance -> completion."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from validate_request_doc import current_document_text

START = "<!-- vk:lifecycle:start -->"
END = "<!-- vk:lifecycle:end -->"
STAGES = (
    "awaiting_confirmation", "ready", "in_progress", "testing",
    "completed_pending_acceptance", "accepted", "completed",
    "blocked", "deferred", "cancelled",
)
FORWARD = dict(zip(STAGES[:6], STAGES[1:7]))


def extract(text: str) -> dict | None:
    text = current_document_text(text)
    if START not in text and END not in text:
        return None
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("expected exactly one lifecycle block in the current requirement")
    match = re.search(re.escape(START) + r"\s*```json\s*\n(.*?)\n```\s*" + re.escape(END), text, re.S)
    if not match:
        raise ValueError("lifecycle block must contain one fenced JSON object")
    data = json.loads(match[1])
    if not isinstance(data, dict):
        raise ValueError("lifecycle must be a JSON object")
    return data


def replace(text: str, data: dict) -> str:
    start, end = text.index(START), text.index(END) + len(END)
    block = START + "\n```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```\n" + END
    return text[:start] + block + text[end:]


def nonempty(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def timestamp(value) -> datetime:
    if not nonempty(value):
        raise ValueError("missing timestamp")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return result


def validate(data: dict, gate: str | None = None, previous: dict | None = None) -> list[str]:
    """Check declared evidence and traceability, not the truth of external tests."""
    errors = []
    try:
        status = data["status"]
        if type(data["schema_version"]) is not int or data["schema_version"] != 1 or status not in STAGES:
            raise ValueError("unsupported schema_version or status")
        if not nonempty(data["task_id"]) or not re.fullmatch(r"I[0-9]{2,}", data["iteration"]) or int(data["iteration"][1:]) == 0:
            raise ValueError("task_id and iteration are required")
        features, criteria = {}, {}
        for feature in data["features"]:
            fid = feature["id"]
            if not nonempty(fid) or fid in features:
                raise ValueError("feature IDs must be unique and nonempty")
            if type(feature["revision"]) is not int or feature["revision"] < 1:
                raise ValueError(f"{fid}: revision must be a positive integer")
            if type(feature["required"]) is not bool or feature["implementation"] not in ("pending", "in_progress", "implemented"):
                raise ValueError(f"{fid}: invalid required/implementation")
            if not nonempty(feature["title"]) or not feature["criteria"]:
                raise ValueError(f"{fid}: title and criteria required")
            features[fid] = feature
            for criterion in feature["criteria"]:
                cid = criterion["id"]
                if not nonempty(cid) or cid in criteria or not nonempty(criterion["description"]):
                    raise ValueError("criterion IDs must be unique with descriptions")
                if type(criterion["required"]) is not bool:
                    raise ValueError(f"{cid}: required must be boolean")
                criteria[cid] = (feature, criterion)
        if not features:
            raise ValueError("at least one feature is required")

        def scoped(record):
            refs = record["criteria"]
            if not refs or len(refs) != len(set(refs)) or any(cid not in criteria for cid in refs):
                raise ValueError(f"{record['id']}: invalid criterion references")
            versions = record["scope_versions"]
            expected = {criteria[cid][0]["id"] for cid in refs}
            if not isinstance(versions, dict) or set(versions) != expected or any(type(v) is not int or v < 1 for v in versions.values()):
                raise ValueError(f"{record['id']}: scope_versions must cover referenced features")
            return all(versions[fid] == features[fid]["revision"] for fid in expected)

        def evidence(record):
            timestamp(record["at"])
            if not nonempty(record["evidence"]):
                raise ValueError(f"{record.get('id', 'record')}: evidence required")

        issues = {}
        for issue in data["issues"]:
            iid = issue["id"]
            if not nonempty(iid) or iid in issues or type(issue["blocking"]) is not bool:
                raise ValueError("issue IDs must be unique; blocking must be boolean")
            if not issue["criteria"] or any(cid not in criteria for cid in issue["criteria"]):
                raise ValueError(f"{iid}: invalid criterion references")
            if issue["source"] not in ("requirements", "development", "review", "testing", "acceptance"):
                raise ValueError(f"{iid}: unknown issue source")
            if issue["status"] not in ("open", "in_progress", "fixed_pending_verification", "verified_resolved", "reopened", "deferred", "not_applicable"):
                raise ValueError(f"{iid}: unknown issue status")
            history = issue["history"]
            if not history or history[-1]["status"] != issue["status"]:
                raise ValueError(f"{iid}: append status transitions to issue history")
            for event in history:
                evidence(event)
            if [timestamp(event["at"]) for event in history] != sorted(timestamp(event["at"]) for event in history):
                raise ValueError(f"{iid}: issue history must be chronological")
            issues[iid] = issue

        tests, runs = {}, {}
        seen_runs = set()
        for test in data["tests"]:
            if not nonempty(test["id"]) or not nonempty(test["run_id"]) or test["run_id"] in seen_runs:
                raise ValueError("test case IDs and unique run_id are required")
            seen_runs.add(test["run_id"])
            runs[test["run_id"]] = test
            scoped(test)
            if type(test["required"]) is not bool or test["status"] not in ("not_run", "pass", "fail", "blocked"):
                raise ValueError(f"{test['id']}: invalid test result")
            if test["status"] != "not_run":
                evidence(test)
                if not nonempty(test["baseline"]):
                    raise ValueError(f"{test['id']}: test baseline required")
            if test["id"] in tests and test["status"] != "not_run" and tests[test["id"]]["status"] != "not_run":
                if timestamp(test["at"]) < timestamp(tests[test["id"]]["at"]):
                    raise ValueError("test runs must be chronological")
            tests[test["id"]] = test

        acceptances, seen_acceptance = {}, set()
        for acceptance in data["acceptance"]:
            if not nonempty(acceptance["id"]) or acceptance["id"] in seen_acceptance:
                raise ValueError("acceptance attempt IDs must be unique")
            seen_acceptance.add(acceptance["id"])
            scoped(acceptance)
            if acceptance["status"] not in ("pending", "pass", "fail", "blocked"):
                raise ValueError("invalid acceptance result")
            if acceptance["status"] != "pending":
                evidence(acceptance)
                if not nonempty(acceptance["by"]) or not nonempty(acceptance["baseline"]):
                    raise ValueError("acceptance actor and reviewed baseline required")
                if acceptance["mechanism"] not in ("user", "agreed"):
                    raise ValueError("acceptance must be by user or agreed mechanism")
                if acceptance["mechanism"] == "agreed" and not nonempty(acceptance.get("agreement")):
                    raise ValueError("agreed acceptance requires the prior agreement")
                if acceptance["status"] == "pass":
                    for cid in acceptance["criteria"]:
                        fid = criteria[cid][0]["id"]
                        if not any(test["status"] == "pass" and cid in test["criteria"]
                                   and test["scope_versions"][fid] == acceptance["scope_versions"][fid]
                                   and test["baseline"] == acceptance["baseline"]
                                   and timestamp(test["at"]) <= timestamp(acceptance["at"])
                                   for test in data["tests"]):
                            raise ValueError(f"{cid}: acceptance must follow passing tests on the accepted scope/baseline")
            for cid in acceptance["criteria"]:
                if cid in acceptances and acceptance["status"] != "pending" and acceptances[cid]["status"] != "pending":
                    if timestamp(acceptance["at"]) < timestamp(acceptances[cid]["at"]):
                        raise ValueError("acceptance attempts must be chronological")
                acceptances[cid] = acceptance

        for record in data["tests"] + data["acceptance"]:
            if record["status"] in ("fail", "blocked"):
                issue = issues.get(record.get("issue_id"))
                if issue is None or not set(record["criteria"]).issubset(issue["criteria"]):
                    raise ValueError(f"{record['id']}: failed/blocked result must link a recorded issue covering its criteria")
        for record in list(tests.values()) + list(acceptances.values()):
            if record["status"] in ("fail", "blocked"):
                issue = issues[record["issue_id"]]
                if issue["status"] in ("verified_resolved", "not_applicable") and timestamp(record["at"]) > timestamp(issue["history"][-1]["at"]):
                    raise ValueError(f"{issue['id']}: latest failure requires reopening the same issue")

        def passing(test):
            return test["status"] == "pass" and scoped(test) and test["baseline"] == data.get("baseline")

        for issue in issues.values():
            if issue["status"] == "verified_resolved":
                resolution = issue["resolution"]
                evidence(resolution)
                if resolution["kind"] not in ("repair", "requirement_change"):
                    raise ValueError("resolved issue needs a repair or requirement-change decision")
                if timestamp(resolution["at"]) < timestamp(issue["history"][0]["at"]):
                    raise ValueError("repair cannot predate issue discovery")
                reruns = [runs[run_id] for run_id in issue["retest_runs"]]
                expected_features = {criteria[cid][0]["id"] for cid in issue["criteria"]}
                if set(resolution["scope_versions"]) != expected_features:
                    raise ValueError("resolution scope_versions must cover affected features")
                covered = set()
                for test in reruns:
                    if test["status"] != "pass" or test["baseline"] != resolution["baseline"] or timestamp(test["at"]) < timestamp(resolution["at"]):
                        raise ValueError(f"{issue['id']}: repair requires passing retests after the repair on its recorded baseline")
                    for fid in expected_features.intersection(test["scope_versions"]):
                        if test["scope_versions"][fid] != resolution["scope_versions"][fid]:
                            raise ValueError("retest scope differs from the recorded repair scope")
                    if timestamp(issue["history"][-1]["at"]) < timestamp(test["at"]):
                        raise ValueError("verified resolution must be recorded after retesting")
                    covered.update(test["criteria"])
                if not set(issue["criteria"]).issubset(covered):
                    raise ValueError(f"{issue['id']}: retests must cover all affected criteria")

        events = data["events"]
        if not events:
            raise ValueError("workflow events are required")
        for event in events:
            evidence(event)
            if event["status"] not in STAGES:
                raise ValueError("event has unknown stage")
        if events[-1]["status"] != status:
            raise ValueError("latest workflow event must match current status")
        if [timestamp(event["at"]) for event in events] != sorted(timestamp(event["at"]) for event in events):
            raise ValueError("workflow events must be chronological")

        if previous is not None:
            for key in ("tests", "acceptance", "events"):
                old = previous[key]
                if data[key][:len(old)] != old:
                    raise ValueError(f"{key} is append-only; preserve prior attempts/events")
            if data["task_id"] != previous["task_id"]:
                raise ValueError("task identity cannot change")
            old_features = {item["id"]: item for item in previous["features"]}
            for fid, old in old_features.items():
                if fid not in features:
                    raise ValueError("preserve removed features with required=false and a change reason")
                new = features[fid]
                if new["revision"] < old["revision"]:
                    raise ValueError("feature scope revision cannot decrease")
                if any(new[key] != old[key] for key in ("title", "criteria", "required")) and new["revision"] <= old["revision"]:
                    raise ValueError("requirement changes must increase affected feature scope revision")
            for old in previous["issues"]:
                new = issues.get(old["id"])
                if not new or new["history"][:len(old["history"])] != old["history"]:
                    raise ValueError("preserve issue IDs and append-only issue histories")
            old_status = previous["status"]
            if old_status != status:
                if len(events) == len(previous["events"]):
                    raise ValueError("stage transitions require a new workflow event")
                early = STAGES[:4]
                returning = status in STAGES[7:] or (status in early and (
                    old_status in STAGES[7:] or STAGES.index(status) <= STAGES.index(old_status)))
                if not returning and FORWARD.get(old_status) != status:
                    raise ValueError(f"cannot skip stages: {old_status} -> {status}")

        target = gate or status
        if target not in STAGES:
            raise ValueError("unknown target gate")
        rank = STAGES.index(target) if target in STAGES[:7] else 0
        required = {cid for cid, (feature, criterion) in criteria.items() if feature["required"] and criterion["required"]}
        if rank >= 1:
            confirmation = data["confirmation"]
            evidence(confirmation)
            if not nonempty(confirmation["by"]) or confirmation["scope_versions"] != {fid: feature["revision"] for fid, feature in features.items()}:
                raise ValueError("scope confirmation must identify the confirmer and current feature versions")
            if not required:
                raise ValueError("confirmed delivery needs at least one required criterion")
        if rank >= 3:
            if not nonempty(data.get("baseline")):
                raise ValueError("testing requires a code/worktree baseline")
            for feature in features.values():
                if feature["required"] and (feature["implementation"] != "implemented" or not nonempty(feature.get("implementation_evidence"))):
                    errors.append(f"{feature['id']}: required implementation is incomplete")
            for cid in required:
                if not any(test["required"] and cid in test["criteria"] and scoped(test) for test in tests.values()):
                    errors.append(f"{cid}: missing required test coverage")
        if rank >= 4:
            for test in tests.values():
                if test["required"] and any(cid in required for cid in test["criteria"]) and not passing(test):
                    errors.append(f"{test['id']}: required test is unrun, failed, blocked, or stale")
            for issue in issues.values():
                if issue["blocking"] and issue["status"] not in ("verified_resolved", "not_applicable"):
                    errors.append(f"{issue['id']}: unresolved blocking issue")
        if rank >= 5:
            for cid in required:
                acceptance = acceptances.get(cid)
                if not acceptance or acceptance["status"] != "pass" or not scoped(acceptance):
                    errors.append(f"{cid}: current scope has not passed acceptance")
                    continue
                for issue in issues.values():
                    if cid in issue["criteria"] and timestamp(acceptance["at"]) < timestamp(issue["history"][-1]["at"]):
                        errors.append(f"{cid}: acceptance predates issue handling; accept again after retesting")
        if target == status and rank >= 4:
            decided = [timestamp(test["at"]) for test in tests.values() if test["required"] and test["status"] == "pass"]
            if rank >= 5:
                decided += [timestamp(record["at"]) for record in acceptances.values() if record["status"] == "pass"]
            if decided and timestamp(events[-1]["at"]) < max(decided):
                errors.append("stage handoff must follow its testing/acceptance evidence")
        if rank >= 6:
            closure = data["closure"]
            evidence(closure)
            if not nonempty(closure["by"]) or closure["documents_synced"] is not True:
                errors.append("completion requires a documented synchronization/closure check")
            finished = [timestamp(record["at"]) for record in acceptances.values() if record["status"] == "pass"]
            finished += [timestamp(test["at"]) for test in tests.values() if test["status"] == "pass"]
            if finished and timestamp(closure["at"]) < max(finished):
                errors.append("closure must follow testing and acceptance")
            if target == status and timestamp(events[-1]["at"]) < timestamp(closure["at"]):
                errors.append("completed event must follow the closure check")
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        errors.append(f"invalid lifecycle: {exc}")
    return errors


def check_document(text: str, *, status: str | None = None, task_id: str | None = None,
                   iteration: str | None = None, gate: str | None = None,
                   previous: dict | None = None) -> list[str]:
    try:
        data = extract(text)
        if data is None:
            return ["missing lifecycle block; attach the ledger to the canonical requirement"]
        errors = validate(data, gate, previous)
        for key, value in (("status", status), ("task_id", task_id), ("iteration", iteration)):
            if value is not None and data.get(key) != value:
                errors.append(f"document {key} disagrees with lifecycle {key}")
        return errors
    except ValueError as exc:
        return [str(exc)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    parser.add_argument("--gate", choices=("current", "ready", "testing", "completed_pending_acceptance", "accepted", "completed"), default="current")
    args = parser.parse_args()
    try:
        text = Path(args.path).read_text(encoding="utf-8")
        metadata = {}
        if text.startswith("---\n"):
            if "\n---\n" not in text:
                raise ValueError("unclosed document frontmatter")
            header = text.split("\n---\n", 1)[0]
            for key in ("status", "task_id", "iteration"):
                match = re.search(r"^" + key + r":\s*(.*?)\s*$", header, re.M)
                if match:
                    metadata[key] = match[1].strip("\"'")
        errors = check_document(text, gate=None if args.gate == "current" else args.gate, **metadata)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    print("LIFECYCLE_STATUS=" + ("FAIL" if errors else "PASS"))
    for error in errors:
        print("FAIL: " + error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
