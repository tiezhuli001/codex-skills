from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
PREPARE = SKILL_ROOT / "scripts" / "prepare_tmp_workspace.py"
SUPPORT_SPLIT = SKILL_ROOT / "scripts" / "support_split_census.py"
TEST_SURFACE = SKILL_ROOT / "scripts" / "test_surface_census.py"
COMPLEXITY = SKILL_ROOT / "scripts" / "complexity_budget_census.py"


class WorkspaceAndCliTests(unittest.TestCase):
    def test_prepare_tmp_workspace_records_explicit_repo_root_in_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "target-repo"
            repo_root.mkdir()
            completed = subprocess.run(
                ["python3", str(PREPARE), "--repo-root", str(repo_root)],
                check=True,
                capture_output=True,
                text=True,
            )
            run_root = Path(completed.stdout.strip())
            manifest = json.loads((run_root / "reports" / "run_manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(Path(manifest["repo_root"]).resolve(), repo_root.resolve())

    def test_prepare_tmp_workspace_help_exits_cleanly(self) -> None:
        completed = subprocess.run(
            ["python3", str(PREPARE), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0)
        self.assertIn("usage", completed.stdout.lower())

    def test_support_split_help_exits_cleanly(self) -> None:
        self._assert_help_works(SUPPORT_SPLIT)

    def test_test_surface_help_exits_cleanly(self) -> None:
        self._assert_help_works(TEST_SURFACE)

    def test_complexity_budget_help_exits_cleanly(self) -> None:
        self._assert_help_works(COMPLEXITY)

    def test_support_split_uses_repo_root_from_manifest(self) -> None:
        payload = self._run_script_with_manifest_repo_root(SUPPORT_SPLIT, repo_kind="support")
        self.assertEqual(Path(payload["repo_root"]).resolve(), Path(self._last_repo_root).resolve())
        self.assertEqual(payload["paths"][0]["path"], "src/helper_support.py")

    def test_test_surface_uses_repo_root_from_manifest(self) -> None:
        payload = self._run_script_with_manifest_repo_root(TEST_SURFACE, repo_kind="tests")
        self.assertEqual(Path(payload["repo_root"]).resolve(), Path(self._last_repo_root).resolve())
        by_path = {entry["path"]: entry for entry in payload["families"]}
        self.assertIn("tests/runtime_family", by_path)
        self.assertEqual(by_path["tests/runtime_family"]["file_count"], 1)

    def test_complexity_budget_uses_repo_root_from_manifest(self) -> None:
        payload = self._run_script_with_manifest_repo_root(COMPLEXITY, repo_kind="complexity")
        self.assertEqual(Path(payload["repo_root"]).resolve(), Path(self._last_repo_root).resolve())
        paths = {entry["path"] for entry in payload["files"]}
        self.assertIn("src/runtime.py", paths)
        self.assertIn("tests/test_runtime.py", paths)

    def _assert_help_works(self, script: Path) -> None:
        completed = subprocess.run(
            ["python3", str(script), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0)
        self.assertIn("usage", completed.stdout.lower())

    def _run_script_with_manifest_repo_root(self, script: Path, repo_kind: str) -> dict:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root = tmp / "target-repo"
            run_root = tmp / "run" / "20260428T000000Z"
            reports_dir = run_root / "reports"
            repo_root.mkdir(parents=True)
            reports_dir.mkdir(parents=True)
            self._build_repo_fixture(repo_root, repo_kind)
            (reports_dir / "run_manifest.json").write_text(
                json.dumps({"repo_root": str(repo_root)}, ensure_ascii=False),
                encoding="utf-8",
            )
            subprocess.run(
                ["python3", str(script), str(run_root)],
                check=True,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self._last_repo_root = str(repo_root.resolve())
            out_name = {
                SUPPORT_SPLIT: "support_split_census.json",
                TEST_SURFACE: "test_surface_census.json",
                COMPLEXITY: "complexity_budget_census.json",
            }[script]
            return json.loads((reports_dir / out_name).read_text(encoding="utf-8"))

    def _build_repo_fixture(self, repo_root: Path, repo_kind: str) -> None:
        (repo_root / "src").mkdir()
        (repo_root / "tests").mkdir()
        if repo_kind == "support":
            (repo_root / "src" / "helper_support.py").write_text(
                "def helper():\n    return 1\n",
                encoding="utf-8",
            )
            (repo_root / "src" / "consumer.py").write_text(
                "from helper_support import helper\n",
                encoding="utf-8",
            )
            (repo_root / "tests" / "test_helper.py").write_text(
                "from helper_support import helper\n\n"
                "def test_helper():\n    assert helper() == 1\n",
                encoding="utf-8",
            )
        elif repo_kind == "tests":
            (repo_root / "tests" / "runtime_family").mkdir()
            (repo_root / "tests" / "runtime_family" / "test_flow.py").write_text(
                "def test_flow():\n    assert True\n",
                encoding="utf-8",
            )
        elif repo_kind == "complexity":
            (repo_root / "src" / "runtime.py").write_text(
                "def run(flag):\n"
                "    if flag:\n"
                "        return 1\n"
                "    return 0\n",
                encoding="utf-8",
            )
            (repo_root / "tests" / "test_runtime.py").write_text(
                "def test_run():\n    assert True\n",
                encoding="utf-8",
            )
        else:
            raise ValueError(repo_kind)


if __name__ == "__main__":
    unittest.main()
