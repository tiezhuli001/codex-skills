from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
EXTERNALIZE = SKILL_ROOT / "scripts" / "externalize_repo_artifacts.py"
FALLBACK = SKILL_ROOT / "scripts" / "fallback_exception_census.py"
REACHABILITY = SKILL_ROOT / "scripts" / "symbol_reachability_census.py"
REPO_SCAN = SKILL_ROOT / "scripts" / "repo_scan_snapshot.sh"
GITNEXUS = SKILL_ROOT / "scripts" / "run_gitnexus_snapshot.sh"


class RunRootToolsTests(unittest.TestCase):
    def test_externalize_help_exits_cleanly(self) -> None:
        self._assert_help_works(["python3", str(EXTERNALIZE)])

    def test_fallback_help_exits_cleanly(self) -> None:
        self._assert_help_works(["python3", str(FALLBACK)])

    def test_reachability_help_exits_cleanly(self) -> None:
        self._assert_help_works(["python3", str(REACHABILITY)])

    def test_repo_scan_help_exits_cleanly(self) -> None:
        self._assert_help_works([str(REPO_SCAN)])

    def test_gitnexus_help_exits_cleanly(self) -> None:
        self._assert_help_works([str(GITNEXUS)])

    def test_externalize_uses_repo_root_from_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root, run_root = self._make_run(tmp)
            (repo_root / "scratch.log").write_text("noise\n", encoding="utf-8")
            subprocess.run(
                ["python3", str(EXTERNALIZE), str(run_root), "scratch.log"],
                check=True,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            payload = self._read_report(run_root, "artifact_externalization.json")

            self.assertEqual(Path(payload["repo_root"]).resolve(), repo_root.resolve())
            self.assertEqual(payload["moved"][0]["from"], "scratch.log")
            self.assertTrue((run_root / "artifacts" / "scratch.log").exists())
            self.assertFalse((repo_root / "scratch.log").exists())

    def test_fallback_exception_census_uses_repo_root_from_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root, run_root = self._make_run(tmp)
            (repo_root / "src").mkdir()
            (repo_root / "tests").mkdir()
            (repo_root / "src" / "runtime.py").write_text(
                "def run():\n"
                "    try:\n"
                "        return normalize()\n"
                "    except Exception:\n"
                "        return None\n",
                encoding="utf-8",
            )
            subprocess.run(
                ["python3", str(FALLBACK), str(run_root)],
                check=True,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            payload = self._read_report(run_root, "fallback_exception_census.json")

            self.assertEqual(Path(payload["repo_root"]).resolve(), repo_root.resolve())
            self.assertEqual(payload["findings"][0]["path"], "src/runtime.py")
            self.assertEqual(payload["findings"][0]["broad_exception_count"], 1)
            self.assertIn("normalize", payload["findings"][0]["fallback_keywords"])

    def test_symbol_reachability_census_uses_repo_root_from_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root, run_root = self._make_run(tmp)
            (repo_root / "src").mkdir()
            (repo_root / "tests").mkdir()
            (repo_root / "src" / "runtime.py").write_text(
                "def alive():\n"
                "    return helper()\n\n"
                "def helper():\n"
                "    return 1\n",
                encoding="utf-8",
            )
            (repo_root / "tests" / "test_runtime.py").write_text(
                "from runtime import alive\n\n"
                "def test_alive():\n"
                "    assert alive() == 1\n",
                encoding="utf-8",
            )
            subprocess.run(
                ["python3", str(REACHABILITY), str(run_root)],
                check=True,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            payload = self._read_report(run_root, "symbol_reachability_census.json")

            self.assertEqual(Path(payload["repo_root"]).resolve(), repo_root.resolve())
            by_name = {item["name"]: item for item in payload["symbols"]}
            self.assertIn("alive", by_name)
            self.assertIn("helper", by_name)
            self.assertEqual(by_name["alive"]["path"], "src/runtime.py")

    def test_repo_scan_snapshot_uses_repo_root_from_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root, run_root = self._make_run(tmp)
            subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
            (repo_root / "tracked.txt").write_text("hello\n", encoding="utf-8")
            subprocess.run([str(REPO_SCAN), str(run_root)], check=True, capture_output=True, text=True, cwd=tmp)
            payload = self._read_report(run_root, "repo_scan_snapshot.json")

            self.assertEqual(Path(payload["repo_root"]).resolve(), repo_root.resolve())
            self.assertEqual(payload["tool_name"], "repo_scan_snapshot")
            self.assertIn("tracked.txt", "\n".join(payload["git_status"]))

    def test_run_gitnexus_snapshot_uses_repo_root_from_manifest_and_externalizes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root, run_root = self._make_run(tmp)
            subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
            (repo_root / ".gitnexus").write_text("cache\n", encoding="utf-8")
            (repo_root / "gitnexus.json").write_text("{}\n", encoding="utf-8")
            (repo_root / ".gitnexus-cache").mkdir()
            fake_bin = tmp / "bin"
            fake_bin.mkdir()
            fake_gitnexus = fake_bin / "gitnexus"
            fake_gitnexus.write_text("#!/bin/sh\necho fake-gitnexus-status\n", encoding="utf-8")
            fake_gitnexus.chmod(fake_gitnexus.stat().st_mode | stat.S_IEXEC)
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}:{env['PATH']}"

            subprocess.run([str(GITNEXUS), str(run_root)], check=True, capture_output=True, text=True, cwd=tmp, env=env)
            payload = self._read_report(run_root, "gitnexus_snapshot.json")

            self.assertEqual(Path(payload["repo_root"]).resolve(), repo_root.resolve())
            self.assertEqual(payload["status"], "available")
            self.assertTrue(any(note.startswith("externalized:") for note in payload["notes"]))
            self.assertTrue((run_root / "artifacts" / ".gitnexus").exists())
            self.assertTrue((run_root / "artifacts" / ".gitnexus-cache").exists())
            self.assertTrue((run_root / "artifacts" / "gitnexus.json").exists())

    def _assert_help_works(self, command: list[str]) -> None:
        completed = subprocess.run(command + ["--help"], check=False, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0)
        self.assertIn("usage", (completed.stdout + completed.stderr).lower())

    def _make_run(self, tmp: Path) -> tuple[Path, Path]:
        repo_root = tmp / "target-repo"
        run_root = tmp / "run" / "20260428T000000Z"
        repo_root.mkdir(parents=True)
        (run_root / "reports").mkdir(parents=True)
        (run_root / "snapshots").mkdir(parents=True)
        (run_root / "logs").mkdir(parents=True)
        (run_root / "artifacts").mkdir(parents=True)
        (run_root / "reports" / "run_manifest.json").write_text(
            json.dumps({"repo_root": str(repo_root)}, ensure_ascii=False),
            encoding="utf-8",
        )
        return repo_root, run_root

    def _read_report(self, run_root: Path, name: str) -> dict:
        return json.loads((run_root / "reports" / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
