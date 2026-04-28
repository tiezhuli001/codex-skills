from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
RUN_FULL_AUDIT = SKILL_ROOT / "scripts" / "run_full_audit.py"


class RunFullAuditTests(unittest.TestCase):
    def test_run_full_audit_help_exits_cleanly(self) -> None:
        completed = subprocess.run(
            ["python3", str(RUN_FULL_AUDIT), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("usage", completed.stdout.lower())

    def test_run_full_audit_generates_core_reports_from_non_repo_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root = tmp / "target-repo"
            repo_root.mkdir()
            subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
            (repo_root / "src").mkdir()
            (repo_root / "tests").mkdir()
            (repo_root / "docs").mkdir()
            (repo_root / "src" / "helper_support.py").write_text(
                "def helper():\n    return 1\n",
                encoding="utf-8",
            )
            (repo_root / "src" / "runtime.py").write_text(
                "def alive():\n    return helper()\n\n"
                "def helper():\n    return 1\n",
                encoding="utf-8",
            )
            (repo_root / "tests" / "test_runtime.py").write_text(
                "from runtime import alive\n\n"
                "def test_alive():\n    assert alive() == 1\n",
                encoding="utf-8",
            )
            (repo_root / "docs" / "README.md").write_text("# Repo\n", encoding="utf-8")
            run_root = tmp / "audit-run"

            subprocess.run(
                [
                    "python3",
                    str(RUN_FULL_AUDIT),
                    "--repo-root",
                    str(repo_root),
                    "--run-root",
                    str(run_root),
                    "--profile",
                    "repo-scan",
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=tmp,
            )

            expected_reports = [
                "run_manifest.json",
                "repo_scan_snapshot.json",
                "repo_surface.json",
                "single_consumer_census.json",
                "support_split_census.json",
                "test_surface_census.json",
                "complexity_budget_census.json",
                "fallback_exception_census.json",
                "symbol_reachability_census.json",
                "symbol_reference_census.json",
                "duplicate_symbol_census.json",
                "thin_wrapper_census.json",
                "test_owner_map.json",
                "production_path_proof.json",
                "gitnexus_snapshot.json",
                "candidate_score_report.json",
                "wave_stability_report.json",
                "cleanup_execution_package.md",
            ]
            for name in expected_reports:
                report = run_root / "reports" / name
                self.assertTrue(report.exists(), name)
                if report.suffix == ".json":
                    payload = json.loads(report.read_text(encoding="utf-8"))
                    if "repo_root" in payload:
                        self.assertEqual(Path(payload["repo_root"]).resolve(), repo_root.resolve())
                else:
                    text = report.read_text(encoding="utf-8")
                    self.assertIn("## Delete-Ready Now", text)
                    self.assertIn("## Cleanup Execution Package", text)

            manifest = json.loads((run_root / "reports" / "run_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["repo_root"], str(repo_root.resolve()))


if __name__ == "__main__":
    unittest.main()
