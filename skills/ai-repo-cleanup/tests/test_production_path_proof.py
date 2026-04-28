from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
PROOF = SKILL_ROOT / "scripts" / "production_path_proof.py"


class ProductionPathProofTests(unittest.TestCase):
    def test_production_path_proof_help_exits_cleanly(self) -> None:
        completed = subprocess.run(["python3", str(PROOF), "--help"], check=False, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0)
        self.assertIn("usage", completed.stdout.lower())

    def test_production_path_proof_reports_importers_and_registration_sites(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root = tmp / "repo"
            run_root = tmp / "run" / "20260428T000000Z"
            (repo_root / "src").mkdir(parents=True)
            (repo_root / "tests").mkdir(parents=True)
            (run_root / "reports").mkdir(parents=True)
            (run_root / "reports" / "run_manifest.json").write_text(json.dumps({"repo_root": str(repo_root)}), encoding="utf-8")
            (run_root / "reports" / "support_split_census.json").write_text(json.dumps({
                "paths": [
                    {"path": "src/helper_support.py", "kind": "helper_support", "real_consumers": 1, "test_consumers": 1, "notes": "candidate only"}
                ]
            }), encoding="utf-8")
            (repo_root / "src" / "helper_support.py").write_text(
                "class HelperSupport:\n    pass\n\n"
                "def build_helper_support():\n    return HelperSupport()\n",
                encoding="utf-8",
            )
            (repo_root / "src" / "bootstrap.py").write_text(
                "from helper_support import build_helper_support\n\n"
                "def register_runtime():\n    helper = build_helper_support()\n    register_helper(helper)\n",
                encoding="utf-8",
            )
            (repo_root / "tests" / "test_helper_support.py").write_text(
                "from helper_support import build_helper_support\n",
                encoding="utf-8",
            )
            subprocess.run(["python3", str(PROOF), "--run-root", str(run_root)], check=True, capture_output=True, text=True)
            payload = json.loads((run_root / "reports" / "production_path_proof.json").read_text(encoding="utf-8"))

        item = payload["items"][0]
        self.assertEqual(item["path"], "src/helper_support.py")
        self.assertIn("src/bootstrap.py", item["caller_proof"]["production_importers"])
        self.assertIn("src/bootstrap.py", item["registration_sites"])
        self.assertIn("src/bootstrap.py", item["constructor_sites"])
        self.assertIn(item["current_owner_confidence"], {"live-boundary", "merge-back-candidate"})


if __name__ == "__main__":
    unittest.main()
