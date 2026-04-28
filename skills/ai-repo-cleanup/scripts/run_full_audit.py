#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CORE_REPORTS = {
    "repo_scan_snapshot": "repo_scan_snapshot.json",
    "repo_surface_snapshot": "repo_surface.json",
    "single_consumer_census": "single_consumer_census.json",
    "support_split_census": "support_split_census.json",
    "test_surface_census": "test_surface_census.json",
    "complexity_budget_census": "complexity_budget_census.json",
    "fallback_exception_census": "fallback_exception_census.json",
    "symbol_reachability_census": "symbol_reachability_census.json",
    "symbol_reference_census": "symbol_reference_census.json",
    "duplicate_symbol_census": "duplicate_symbol_census.json",
    "thin_wrapper_census": "thin_wrapper_census.json",
    "test_owner_map": "test_owner_map.json",
    "production_path_proof": "production_path_proof.json",
    "run_gitnexus_snapshot": "gitnexus_snapshot.json",
    "score_cleanup_candidates": "candidate_score_report.json",
    "compare_cleanup_runs": "wave_stability_report.json",
    "render_cleanup_package": "cleanup_execution_package.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one full ai-repo-cleanup repo scan and write all reports under one run_root.")
    parser.add_argument("--repo-root", required=True, help="Target repository root to audit.")
    parser.add_argument("--run-root", default=None, help="Existing or new run_root directory. Defaults to /tmp/skill/ai-repo-cleanup/runs/<timestamp>.")
    parser.add_argument("--profile", choices=["repo-scan"], default="repo-scan", help="Audit profile to execute.")
    return parser.parse_args()


def _default_run_root() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path("/tmp/skill/ai-repo-cleanup/runs") / stamp


def _write_manifest(run_root: Path, repo_root: Path, profile: str, generated_reports: list[str] | None = None) -> None:
    manifest = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool_name": "run_full_audit",
        "schema_version": 1,
        "run_root": str(run_root),
        "reports_dir": str(run_root / "reports"),
        "artifacts_dir": str(run_root / "artifacts"),
        "snapshots_dir": str(run_root / "snapshots"),
        "logs_dir": str(run_root / "logs"),
        "repo_root": str(repo_root),
        "delivery_mode": "cleanup-execution-handoff",
        "audit_scope": profile,
        "single_live_checklist": True,
        "generated_reports": generated_reports or [],
    }
    out = run_root / "reports" / "run_manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _run(command: list[str], *, cwd: Path) -> None:
    subprocess.run(command, check=True, cwd=cwd)


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    run_root = Path(args.run_root).expanduser().resolve() if args.run_root else _default_run_root().resolve()
    for name in ("artifacts", "reports", "snapshots", "logs"):
        (run_root / name).mkdir(parents=True, exist_ok=True)
    _write_manifest(run_root, repo_root, args.profile)

    py = sys.executable
    repo_scan_reports = run_root / "reports"
    _run([py, str(SCRIPT_DIR / "repo_scan_snapshot.py"), str(run_root), "--repo-root", str(repo_root)], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "repo_surface_snapshot.py"), "--root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["repo_surface_snapshot"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "single_consumer_census.py"), "--root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["single_consumer_census"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "support_split_census.py"), str(run_root), "--repo-root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["support_split_census"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "test_surface_census.py"), str(run_root), "--repo-root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["test_surface_census"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "complexity_budget_census.py"), str(run_root), "--repo-root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["complexity_budget_census"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "fallback_exception_census.py"), str(run_root), "--repo-root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["fallback_exception_census"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "symbol_reachability_census.py"), str(run_root), "--repo-root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["symbol_reachability_census"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "symbol_reference_census.py"), "--root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["symbol_reference_census"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "duplicate_symbol_census.py"), "--root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["duplicate_symbol_census"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "thin_wrapper_census.py"), "--run-root", str(run_root), "--repo-root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["thin_wrapper_census"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "test_owner_map.py"), "--run-root", str(run_root), "--repo-root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["test_owner_map"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "production_path_proof.py"), "--run-root", str(run_root), "--repo-root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["production_path_proof"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "run_gitnexus_snapshot.py"), str(run_root), "--repo-root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["run_gitnexus_snapshot"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "score_cleanup_candidates.py"), "--run-root", str(run_root), "--repo-root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["score_cleanup_candidates"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "compare_cleanup_runs.py"), "--run-root", str(run_root), "--repo-root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["compare_cleanup_runs"])], cwd=SCRIPT_DIR)
    _run([py, str(SCRIPT_DIR / "render_cleanup_package.py"), "--run-root", str(run_root), "--repo-root", str(repo_root), "--out", str(repo_scan_reports / CORE_REPORTS["render_cleanup_package"])], cwd=SCRIPT_DIR)

    generated_reports = ["run_manifest.json", *CORE_REPORTS.values()]
    _write_manifest(run_root, repo_root, args.profile, generated_reports=generated_reports)
    print(str(run_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
