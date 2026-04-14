from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SINGLE_CONSUMER = SKILL_ROOT / "scripts" / "single_consumer_census.py"
DUPLICATE_SYMBOL = SKILL_ROOT / "scripts" / "duplicate_symbol_census.py"
SYMBOL_REFERENCE = SKILL_ROOT / "scripts" / "symbol_reference_census.py"


class CandidateCensusScriptTests(unittest.TestCase):
    def test_single_consumer_census_finds_single_import_consumer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "src").mkdir()
            (root / "tests").mkdir()
            (root / "src" / "helper_adapter.py").write_text(
                "def run():\n    return 1\n",
                encoding="utf-8",
            )
            (root / "tests" / "test_use.py").write_text(
                "from src.helper_adapter import run\n\n"
                "def test_run():\n    assert run() == 1\n",
                encoding="utf-8",
            )
            out = root / "reports" / "single_consumer.json"
            subprocess.run(["python3", str(SINGLE_CONSUMER), "--root", str(root), "--out", str(out)], check=True)
            payload = json.loads(out.read_text(encoding="utf-8"))

        item = next(entry for entry in payload["items"] if entry["path"] == "src/helper_adapter.py")
        self.assertEqual(item["consumer_count"], 1)
        self.assertEqual(item["consumers"], ["tests/test_use.py"])
        self.assertIn("single-consumer-support-split", item["signals"])

    def test_duplicate_symbol_census_groups_duplicate_functions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "a.py").write_text(
                "def write_skill(root, skill_id, body):\n    return (root, skill_id, body)\n",
                encoding="utf-8",
            )
            (root / "b.py").write_text(
                "def emit_skill(root, skill_id, body):\n    return (root, skill_id, body)\n",
                encoding="utf-8",
            )
            out = root / "reports" / "duplicate_symbol.json"
            subprocess.run(["python3", str(DUPLICATE_SYMBOL), "--root", str(root), "--out", str(out)], check=True)
            payload = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(len(payload["duplicate_groups"]), 1)
        symbols = {item["symbol"] for item in payload["duplicate_groups"][0]["items"]}
        self.assertEqual(symbols, {"write_skill", "emit_skill"})

    def test_symbol_reference_census_reports_low_external_reference_symbols(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "src").mkdir()
            (root / "tests").mkdir()
            (root / "src" / "runtime.py").write_text(
                "def alive():\n    return helper()\n\n"
                "def helper():\n    return 1\n\n"
                "class Lonely:\n    pass\n",
                encoding="utf-8",
            )
            (root / "tests" / "test_runtime.py").write_text(
                "from src.runtime import alive\n\n"
                "def test_alive():\n    assert alive() == 1\n",
                encoding="utf-8",
            )
            out = root / "reports" / "symbol_reference.json"
            subprocess.run(["python3", str(SYMBOL_REFERENCE), "--root", str(root), "--out", str(out)], check=True)
            payload = json.loads(out.read_text(encoding="utf-8"))

        by_symbol = {item["symbol"]: item for item in payload["items"]}
        self.assertIn("helper", by_symbol)
        self.assertEqual(by_symbol["helper"]["external_refs"], 0)
        self.assertIn("no-external-references", by_symbol["helper"]["signals"])
        self.assertIn("Lonely", by_symbol)
        self.assertEqual(by_symbol["Lonely"]["external_refs"], 0)


if __name__ == "__main__":
    unittest.main()
