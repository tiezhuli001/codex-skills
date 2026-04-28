from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
COMPARE = SKILL_ROOT / "scripts" / "compare_cleanup_runs.py"


class WaveStabilityTests(unittest.TestCase):
    def test_compare_cleanup_runs_help_exits_cleanly(self) -> None:
        completed = subprocess.run(["python3", str(COMPARE), "--help"], check=False, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0)
        self.assertIn("usage", completed.stdout.lower())

    def test_compare_cleanup_runs_reports_new_promoted_and_resolved_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root = tmp / "repo"
            repo_root.mkdir()
            runs_root = tmp / "runs"
            prev_run = runs_root / "20260427T000000Z"
            curr_run = runs_root / "20260428T000000Z"
            for run_root in (prev_run, curr_run):
                (run_root / "reports").mkdir(parents=True)
                (run_root / "reports" / "run_manifest.json").write_text(
                    json.dumps({"repo_root": str(repo_root), "run_id": run_root.name}),
                    encoding="utf-8",
                )
            (prev_run / "reports" / "candidate_score_report.json").write_text(json.dumps({
                "items": [
                    {"path_or_group": "family-a", "candidate_type": "large-test-family", "priority_band": "aggressive-backlog"},
                    {"path_or_group": "family-b", "candidate_type": "large-test-family", "priority_band": "high-probability-next"},
                ]
            }), encoding="utf-8")
            (curr_run / "reports" / "candidate_score_report.json").write_text(json.dumps({
                "items": [
                    {"path_or_group": "family-a", "candidate_type": "large-test-family", "priority_band": "high-probability-next"},
                    {"path_or_group": "family-c", "candidate_type": "duplicate-symbol", "priority_band": "high-probability-next"},
                ]
            }), encoding="utf-8")

            subprocess.run(["python3", str(COMPARE), "--run-root", str(curr_run)], check=True, capture_output=True, text=True)
            payload = json.loads((curr_run / "reports" / "wave_stability_report.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "compared")
        self.assertEqual(payload["previous_run_id"], "20260427T000000Z")
        self.assertEqual(payload["current_run_id"], "20260428T000000Z")
        self.assertEqual(payload["new_candidates"][0]["path_or_group"], "family-c")
        self.assertEqual(payload["promoted_candidates"][0]["path_or_group"], "family-a")
        self.assertEqual(payload["resolved_candidates"][0]["path_or_group"], "family-b")


if __name__ == "__main__":
    unittest.main()
