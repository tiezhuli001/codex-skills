from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
THIN_WRAPPER = SKILL_ROOT / "scripts" / "thin_wrapper_census.py"
OWNER_MAP = SKILL_ROOT / "scripts" / "test_owner_map.py"


class OverlapAndWrapperTests(unittest.TestCase):
    def test_thin_wrapper_help_exits_cleanly(self) -> None:
        completed = subprocess.run(["python3", str(THIN_WRAPPER), "--help"], check=False, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0)
        self.assertIn("usage", completed.stdout.lower())

    def test_test_owner_map_help_exits_cleanly(self) -> None:
        completed = subprocess.run(["python3", str(OWNER_MAP), "--help"], check=False, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0)
        self.assertIn("usage", completed.stdout.lower())

    def test_thin_wrapper_census_finds_forwarders(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root = tmp / "repo"
            run_root = tmp / "run" / "20260428T000000Z"
            (run_root / "reports").mkdir(parents=True)
            (repo_root / "src").mkdir(parents=True)
            (repo_root / "tests").mkdir(parents=True)
            (run_root / "reports" / "run_manifest.json").write_text(json.dumps({"repo_root": str(repo_root)}), encoding="utf-8")
            (repo_root / "src" / "wrappers.py").write_text(
                "def helper(x):\n    return x\n\n"
                "def forward(x):\n    return helper(x)\n\n"
                "def not_wrapper(x):\n    y = helper(x)\n    return y + 1\n",
                encoding="utf-8",
            )
            subprocess.run(["python3", str(THIN_WRAPPER), "--run-root", str(run_root)], check=True, capture_output=True, text=True)
            payload = json.loads((run_root / "reports" / "thin_wrapper_census.json").read_text(encoding="utf-8"))

        symbols = {item["symbol"]: item for item in payload["items"]}
        self.assertIn("forward", symbols)
        self.assertEqual(symbols["forward"]["target_calls"], ["helper"])
        self.assertNotIn("not_wrapper", symbols)

    def test_test_owner_map_clusters_overlapping_large_test_family(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root = tmp / "repo"
            run_root = tmp / "run" / "20260428T000000Z"
            (run_root / "reports").mkdir(parents=True)
            (repo_root / "tests" / "contracts").mkdir(parents=True)
            (run_root / "reports" / "run_manifest.json").write_text(json.dumps({"repo_root": str(repo_root)}), encoding="utf-8")
            (repo_root / "tests" / "test_gateway.py").write_text(
                "def test_http_messages_endpoint_returns_final_card():\n    assert True\n\n"
                "def test_http_session_resume_switches_session():\n    assert True\n",
                encoding="utf-8",
            )
            (repo_root / "tests" / "contracts" / "test_gateway_contracts.py").write_text(
                "def test_http_messages_contract_keeps_final_card():\n    assert True\n\n"
                "def test_http_messages_contract_keeps_session_shape():\n    assert True\n",
                encoding="utf-8",
            )
            (repo_root / "tests" / "contracts" / "test_runtime_contracts.py").write_text(
                "def test_runtime_diagnostics_keep_session_surface():\n    assert True\n\n"
                "def test_runtime_catalog_keeps_http_tool_surface():\n    assert True\n",
                encoding="utf-8",
            )
            subprocess.run(["python3", str(OWNER_MAP), "--run-root", str(run_root)], check=True, capture_output=True, text=True)
            payload = json.loads((run_root / "reports" / "test_owner_map.json").read_text(encoding="utf-8"))

        self.assertTrue(payload["clusters"])
        cluster = payload["clusters"][0]
        self.assertGreaterEqual(cluster["cluster_size"]["files"], 2)
        self.assertIn("gateway", cluster["path_or_group"])
        self.assertTrue(any("test_gateway.py" in row["path"] for row in cluster["owner_map"]))
        self.assertTrue(cluster["overlap_tokens"])

    def test_test_owner_map_keeps_distinct_path_families_separate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root = tmp / "repo"
            run_root = tmp / "run" / "20260428T000000Z"
            (run_root / "reports").mkdir(parents=True)
            (repo_root / "tests" / "tools").mkdir(parents=True)
            (run_root / "reports" / "run_manifest.json").write_text(json.dumps({"repo_root": str(repo_root)}), encoding="utf-8")
            (repo_root / "tests" / "test_gateway.py").write_text(
                "def test_gateway_session_keeps_final_card():\n    assert True\n\n"
                "def test_gateway_messages_keep_session_shape():\n    assert True\n",
                encoding="utf-8",
            )
            (repo_root / "tests" / "test_gateway_contracts.py").write_text(
                "def test_gateway_contract_keeps_session_card():\n    assert True\n",
                encoding="utf-8",
            )
            (repo_root / "tests" / "test_skills.py").write_text(
                "def test_skill_session_keeps_rendered_card():\n    assert True\n\n"
                "def test_skill_messages_keep_session_shape():\n    assert True\n",
                encoding="utf-8",
            )
            (repo_root / "tests" / "tools" / "test_runtime_and_skill_tools.py").write_text(
                "def test_skill_tool_session_card_stays_visible():\n    assert True\n",
                encoding="utf-8",
            )
            subprocess.run(["python3", str(OWNER_MAP), "--run-root", str(run_root)], check=True, capture_output=True, text=True)
            payload = json.loads((run_root / "reports" / "test_owner_map.json").read_text(encoding="utf-8"))

        names = {cluster["path_or_group"] for cluster in payload["clusters"]}
        self.assertTrue(any("gateway" in name for name in names))
        self.assertTrue(any("skill" in name for name in names))
        self.assertTrue(all(cluster["cluster_size"]["files"] <= 2 for cluster in payload["clusters"]))


if __name__ == "__main__":
    unittest.main()
