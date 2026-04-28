#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from census_utils import read_run_manifest, resolve_repo_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare the current cleanup wave with the previous wave for the same repository.")
    parser.add_argument("--run-root", required=True, help="Current run root created by prepare_tmp_workspace.py or run_full_audit.py")
    parser.add_argument("--repo-root", default=None, help="Target repository root override. Defaults to run_manifest repo_root, then cwd.")
    parser.add_argument("--out", default=None, help="Output JSON path. Defaults to <run_root>/reports/wave_stability_report.json")
    return parser.parse_args()


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _candidate_map(report: dict) -> dict[tuple[str, str], dict]:
    out: dict[tuple[str, str], dict] = {}
    for item in report.get("items", []):
        key = (str(item.get("path_or_group", "")), str(item.get("candidate_type", "")))
        if key[0] and key[1]:
            out[key] = item
    return out


def _previous_run_for_repo(current_run_root: Path, repo_root: Path) -> Path | None:
    runs_root = current_run_root.parent
    if not runs_root.exists():
        return None
    candidates: list[Path] = []
    for sibling in sorted(runs_root.iterdir()):
        if sibling == current_run_root or not sibling.is_dir():
            continue
        manifest = read_run_manifest(sibling)
        sibling_repo = manifest.get("repo_root")
        if isinstance(sibling_repo, str) and Path(sibling_repo).expanduser().resolve() == repo_root.resolve():
            candidates.append(sibling)
    if not candidates:
        return None
    return sorted(candidates)[-1]


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    repo_root = resolve_repo_root(run_root, args.repo_root)
    out = Path(args.out).expanduser().resolve() if args.out else run_root / "reports" / "wave_stability_report.json"
    current = _read_json(run_root / "reports" / "candidate_score_report.json")
    previous_run = _previous_run_for_repo(run_root, repo_root)

    payload = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "compare_cleanup_runs",
        "schema_version": 1,
        "current_run_id": run_root.name,
    }
    if previous_run is None:
        payload.update(
            {
                "status": "no-previous-run",
                "previous_run_id": None,
                "new_candidates": [],
                "promoted_candidates": [],
                "resolved_candidates": [],
                "persistent_candidates": [],
            }
        )
    else:
        previous = _read_json(previous_run / "reports" / "candidate_score_report.json")
        prev_map = _candidate_map(previous)
        curr_map = _candidate_map(current)

        new_candidates = [
            {"path_or_group": key[0], "candidate_type": key[1], "priority_band": item.get("priority_band")}
            for key, item in curr_map.items()
            if key not in prev_map
        ]
        promoted_candidates = [
            {"path_or_group": key[0], "candidate_type": key[1], "from": prev_map[key].get("priority_band"), "to": item.get("priority_band")}
            for key, item in curr_map.items()
            if key in prev_map and prev_map[key].get("priority_band") != item.get("priority_band") and item.get("priority_band") == "high-probability-next"
        ]
        resolved_candidates = [
            {"path_or_group": key[0], "candidate_type": key[1], "previous_priority_band": item.get("priority_band")}
            for key, item in prev_map.items()
            if key not in curr_map
        ]
        persistent_candidates = [
            {"path_or_group": key[0], "candidate_type": key[1], "priority_band": item.get("priority_band")}
            for key, item in curr_map.items()
            if key in prev_map and prev_map[key].get("priority_band") == item.get("priority_band")
        ]
        payload.update(
            {
                "status": "compared",
                "previous_run_id": previous_run.name,
                "new_candidates": new_candidates,
                "promoted_candidates": promoted_candidates,
                "resolved_candidates": resolved_candidates,
                "persistent_candidates": persistent_candidates,
            }
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
