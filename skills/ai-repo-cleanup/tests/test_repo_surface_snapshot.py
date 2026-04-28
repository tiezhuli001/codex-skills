from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "repo_surface_snapshot.py"


class RepoSurfaceSnapshotScriptTests(unittest.TestCase):
    def test_iter_files_prefers_git_tracked_paths(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location("repo_surface_snapshot", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / "tracked.py").write_text("print('x')\n", encoding="utf-8")
            (root / "ignored.log").write_text("noise\n", encoding="utf-8")

            completed = subprocess.CompletedProcess(
                args=["git"],
                returncode=0,
                stdout="tracked.py\n",
                stderr="",
            )
            with patch.object(module.subprocess, "run", return_value=completed):
                paths = list(module.iter_files(root))

        self.assertEqual([path.name for path in paths], ["tracked.py"])

    def test_script_classifies_roles_and_counts_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "app").mkdir()
            (root / "tests").mkdir()
            (root / "docs").mkdir()
            (root / "dist").mkdir()

            (root / "app" / "runtime.py").write_text(
                "def run():\n"
                "    return 1\n",
                encoding="utf-8",
            )
            (root / "tests" / "test_runtime.py").write_text(
                "import unittest\n\n"
                "class TestRuntime(unittest.TestCase):\n"
                "    def test_run(self):\n"
                "        self.assertEqual(1, 1)\n",
                encoding="utf-8",
            )
            (root / "docs" / "README.md").write_text(
                "# Title\n\n"
                "Some docs.\n",
                encoding="utf-8",
            )
            (root / "dist" / "bundle.js").write_text(
                "function main(){return 1;}\n",
                encoding="utf-8",
            )

            out = root / "snapshot.json"
            subprocess.run(
                ["python3", str(SCRIPT), "--root", str(root), "--out", str(out)],
                check=True,
            )

            payload = json.loads(out.read_text(encoding="utf-8"))

        roles = payload["roles"]
        self.assertEqual(Path(payload["repo_root"]).resolve(), root.resolve())
        self.assertEqual(payload["tool_name"], "repo_surface_snapshot")
        self.assertEqual(payload["schema_version"], 1)
        self.assertIn("generated_at", payload)
        self.assertEqual(payload["summary"]["scanned_files"], 4)
        self.assertEqual(roles["production-like"]["files"], 1)
        self.assertEqual(roles["test-like"]["files"], 1)
        self.assertEqual(roles["docs-like"]["files"], 1)
        self.assertEqual(roles["generated-or-vendor"]["files"], 1)
        self.assertEqual(roles["unknown-or-mixed"]["files"], 0)
        self.assertGreater(payload["derived_signals"]["test_like_to_production_like_ratio"], 0)

    def test_script_uses_unknown_when_signals_conflict_or_are_weak(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "misc").mkdir()
            weird = root / "misc" / "notes.data"
            weird.write_text("alpha\nbeta\n", encoding="utf-8")
            out = root / "snapshot.json"
            subprocess.run(
                ["python3", str(SCRIPT), "--root", str(root), "--out", str(out)],
                check=True,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(payload["roles"]["unknown-or-mixed"]["files"], 1)
        self.assertIn("misc/notes.data", payload["top_paths"]["unknown-or-mixed"][0]["path"])


if __name__ == "__main__":
    unittest.main()
