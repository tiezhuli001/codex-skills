from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCORER = SKILL_ROOT / "scripts" / "score_cleanup_candidates.py"


class CandidateScoringTests(unittest.TestCase):
    def test_candidate_scoring_help_exits_cleanly(self) -> None:
        completed = subprocess.run(
            ["python3", str(SCORER), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("usage", completed.stdout.lower())

    def test_candidate_scoring_crosses_signals_and_filters_lonely_low_reference_noise(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root = tmp / "repo"
            repo_root.mkdir()
            run_root = tmp / "run" / "20260428T000000Z"
            reports = run_root / "reports"
            reports.mkdir(parents=True)
            (reports / "run_manifest.json").write_text(json.dumps({"repo_root": str(repo_root)}), encoding="utf-8")
            (reports / "test_surface_census.json").write_text(json.dumps({
                "families": [
                    {"path": "tests/runtime_loop", "file_count": 4, "line_count": 1800, "test_count": 40},
                ]
            }), encoding="utf-8")
            (reports / "duplicate_symbol_census.json").write_text(json.dumps({
                "duplicate_groups": [
                    {"group_id": "dup_1", "match_kind": "ast-equivalent", "items": [
                        {"path": "src/runtime/a.py", "symbol": "helper"},
                        {"path": "src/runtime/b.py", "symbol": "helper"},
                    ], "signals": ["duplicate-implementation"]}
                ]
            }), encoding="utf-8")
            (reports / "support_split_census.json").write_text(json.dumps({
                "paths": [
                    {"path": "src/runtime/helper_support.py", "kind": "helper_support", "real_consumers": 1, "test_consumers": 1, "notes": "candidate only"}
                ]
            }), encoding="utf-8")
            (reports / "single_consumer_census.json").write_text(json.dumps({
                "items": [
                    {"path": "src/runtime/helper_support.py", "role": "production-like", "consumer_count": 1, "consumers": ["src/runtime/main.py"], "signals": ["single-consumer-support-split"]}
                ]
            }), encoding="utf-8")
            (reports / "symbol_reference_census.json").write_text(json.dumps({
                "items": [
                    {"path": "src/runtime/helper_support.py", "symbol": "helper_support", "external_refs": 1, "signals": ["low-external-reference-count"]},
                    {"path": "src/runtime/lonely.py", "symbol": "lonely", "external_refs": 0, "signals": ["no-external-references", "low-external-reference-count"]},
                ]
            }), encoding="utf-8")
            (reports / "symbol_reachability_census.json").write_text(json.dumps({
                "symbols": [
                    {"path": "src/runtime/helper_support.py", "name": "helper_support", "suspicion": "needs-proof", "production_reference_count": 1, "test_reference_count": 1},
                    {"path": "src/runtime/lonely.py", "name": "lonely", "suspicion": "do-not-touch-yet", "production_reference_count": 2, "test_reference_count": 0},
                ]
            }), encoding="utf-8")
            (reports / "fallback_exception_census.json").write_text(json.dumps({
                "findings": [
                    {"path": "src/runtime/helper_support.py", "broad_exception_count": 1, "fallback_keywords": ["compat"], "notes": "signal only"}
                ]
            }), encoding="utf-8")

            subprocess.run(["python3", str(SCORER), "--run-root", str(run_root)], check=True, capture_output=True, text=True)
            payload = json.loads((reports / "candidate_score_report.json").read_text(encoding="utf-8"))

        items = payload["items"]
        by_type = {item["candidate_type"]: item for item in items}
        self.assertIn("large-test-family", by_type)
        self.assertIn("duplicate-symbol", by_type)
        self.assertTrue(any(item["path_or_group"] == "src/runtime/helper_support.py" for item in items))
        self.assertFalse(any("src/runtime/lonely.py" == item["path_or_group"] for item in items))
        helper_item = next(item for item in items if item["path_or_group"] == "src/runtime/helper_support.py")
        self.assertEqual(helper_item["priority_band"], "aggressive-backlog")
        self.assertGreaterEqual(helper_item["score"], 50)

    def test_candidate_scoring_demotes_diffuse_large_test_family_clusters(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root = tmp / "repo"
            repo_root.mkdir()
            run_root = tmp / "run" / "20260428T000000Z"
            reports = run_root / "reports"
            reports.mkdir(parents=True)
            (reports / "run_manifest.json").write_text(json.dumps({"repo_root": str(repo_root)}), encoding="utf-8")
            (reports / "test_owner_map.json").write_text(json.dumps({
                "clusters": [
                    {
                        "path_or_group": "focused-gateway family",
                        "cluster_size": {"files": 3, "lines": 1800, "tests": 40},
                        "overlap_tokens": ["card", "session", "gateway", "http", "message", "final"],
                        "current_round_maturity": "mapping-first",
                    },
                    {
                        "path_or_group": "diffuse-runtime family",
                        "cluster_size": {"files": 9, "lines": 6000, "tests": 90},
                        "overlap_tokens": ["query"],
                        "current_round_maturity": "mapping-first",
                    },
                ]
            }), encoding="utf-8")

            subprocess.run(["python3", str(SCORER), "--run-root", str(run_root)], check=True, capture_output=True, text=True)
            payload = json.loads((reports / "candidate_score_report.json").read_text(encoding="utf-8"))

        by_name = {item["path_or_group"]: item for item in payload["items"]}
        self.assertEqual(by_name["focused-gateway family"]["priority_band"], "high-probability-next")
        self.assertEqual(by_name["diffuse-runtime family"]["priority_band"], "aggressive-backlog")
        self.assertGreater(by_name["focused-gateway family"]["score"], by_name["diffuse-runtime family"]["score"])

    def test_candidate_scoring_caps_high_priority_and_merges_overlapping_owner_clusters(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root = tmp / "repo"
            repo_root.mkdir()
            run_root = tmp / "run" / "20260428T000000Z"
            reports = run_root / "reports"
            reports.mkdir(parents=True)
            (reports / "run_manifest.json").write_text(json.dumps({"repo_root": str(repo_root)}), encoding="utf-8")
            clusters = [
                {
                    "path_or_group": f"family-{idx}",
                    "cluster_size": {"files": 3, "lines": 1800 + idx, "tests": 40},
                    "overlap_tokens": ["card", "session", "message", "final", "gateway", "http"],
                    "current_round_maturity": "mapping-first",
                    "owner_map": [
                        {"path": f"tests/family_{idx}_a.py", "line_count": 600, "dominant_tokens": ["gateway"], "test_count": 10},
                        {"path": f"tests/family_{idx}_b.py", "line_count": 600, "dominant_tokens": ["card"], "test_count": 15},
                        {"path": f"tests/family_{idx}_c.py", "line_count": 600, "dominant_tokens": ["session"], "test_count": 15},
                    ],
                    "first_batch_exact_targets": [f"review overlap around token_{idx}"],
                }
                for idx in range(8)
            ]
            clusters.extend(
                [
                    {
                        "path_or_group": "followup-recovery-runtime family",
                        "cluster_size": {"files": 3, "lines": 2400, "tests": 30},
                        "overlap_tokens": ["followup", "recovery", "runtime", "finalize"],
                        "current_round_maturity": "mapping-first",
                        "owner_map": [
                            {"path": "tests/a.py", "line_count": 800, "dominant_tokens": ["followup"], "test_count": 10},
                            {"path": "tests/b.py", "line_count": 800, "dominant_tokens": ["recovery"], "test_count": 10},
                            {"path": "tests/c.py", "line_count": 800, "dominant_tokens": ["runtime"], "test_count": 10},
                        ],
                        "first_batch_exact_targets": ["review overlap around followup"],
                    },
                    {
                        "path_or_group": "recovery-followup-runtime family",
                        "cluster_size": {"files": 3, "lines": 2500, "tests": 30},
                        "overlap_tokens": ["followup", "recovery", "runtime", "repair"],
                        "current_round_maturity": "mapping-first",
                        "owner_map": [
                            {"path": "tests/a.py", "line_count": 800, "dominant_tokens": ["followup"], "test_count": 10},
                            {"path": "tests/b.py", "line_count": 800, "dominant_tokens": ["recovery"], "test_count": 10},
                            {"path": "tests/d.py", "line_count": 900, "dominant_tokens": ["repair"], "test_count": 10},
                        ],
                        "first_batch_exact_targets": ["review overlap around recovery"],
                    },
                ]
            )
            (reports / "test_owner_map.json").write_text(json.dumps({"clusters": clusters}), encoding="utf-8")

            subprocess.run(["python3", str(SCORER), "--run-root", str(run_root)], check=True, capture_output=True, text=True)
            payload = json.loads((reports / "candidate_score_report.json").read_text(encoding="utf-8"))

        high = [item for item in payload["items"] if item["priority_band"] == "high-probability-next"]
        self.assertLessEqual(len(high), 8)
        merged = [
            item
            for item in payload["items"]
            if item["candidate_type"] == "large-test-family"
            and set(item.get("cluster_files", [])) == {"tests/a.py", "tests/b.py", "tests/c.py", "tests/d.py"}
        ]
        self.assertEqual(len(merged), 1)
        self.assertIn("review overlap around followup", merged[0]["first_batch_exact_targets"])
        self.assertIn("review overlap around recovery", merged[0]["first_batch_exact_targets"])

    def test_candidate_scoring_suggests_canonical_owner_for_duplicate_symbols(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root = tmp / "repo"
            repo_root.mkdir()
            run_root = tmp / "run" / "20260428T000000Z"
            reports = run_root / "reports"
            reports.mkdir(parents=True)
            (reports / "run_manifest.json").write_text(json.dumps({"repo_root": str(repo_root)}), encoding="utf-8")
            (reports / "duplicate_symbol_census.json").write_text(json.dumps({
                "duplicate_groups": [
                    {
                        "group_id": "dup_1",
                        "match_kind": "ast-equivalent",
                        "items": [
                            {"path": "src/runtime/a.py", "symbol": "helper"},
                            {"path": "src/runtime/support/b.py", "symbol": "helper"},
                        ],
                    }
                ]
            }), encoding="utf-8")
            (reports / "symbol_reference_census.json").write_text(json.dumps({
                "items": [
                    {"path": "src/runtime/a.py", "symbol": "helper", "external_refs": 5, "role": "production-like"},
                    {"path": "src/runtime/support/b.py", "symbol": "helper", "external_refs": 1, "role": "production-like"},
                ]
            }), encoding="utf-8")

            subprocess.run(["python3", str(SCORER), "--run-root", str(run_root)], check=True, capture_output=True, text=True)
            payload = json.loads((reports / "candidate_score_report.json").read_text(encoding="utf-8"))

        dup = next(item for item in payload["items"] if item["candidate_type"] == "duplicate-symbol")
        self.assertEqual(dup["canonical_owner"]["path"], "src/runtime/a.py")
        self.assertEqual(dup["canonical_owner"]["external_refs"], 5)

    def test_candidate_scoring_keeps_duplicate_symbols_inside_high_priority_cap(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root = tmp / "repo"
            repo_root.mkdir()
            run_root = tmp / "run" / "20260428T000000Z"
            reports = run_root / "reports"
            reports.mkdir(parents=True)
            (reports / "run_manifest.json").write_text(json.dumps({"repo_root": str(repo_root)}), encoding="utf-8")
            (reports / "test_owner_map.json").write_text(json.dumps({
                "clusters": [
                    {
                        "path_or_group": f"family-{idx}",
                        "cluster_size": {"files": 3, "lines": 2200 + idx, "tests": 40},
                        "overlap_tokens": ["card", "session", "gateway", "message", "final", "http"],
                        "current_round_maturity": "mapping-first",
                        "owner_map": [
                            {"path": f"tests/f_{idx}_a.py", "line_count": 700, "dominant_tokens": ["gateway"], "test_count": 10},
                            {"path": f"tests/f_{idx}_b.py", "line_count": 700, "dominant_tokens": ["card"], "test_count": 15},
                            {"path": f"tests/f_{idx}_c.py", "line_count": 700, "dominant_tokens": ["session"], "test_count": 15},
                        ],
                    }
                    for idx in range(8)
                ]
            }), encoding="utf-8")
            (reports / "duplicate_symbol_census.json").write_text(json.dumps({
                "duplicate_groups": [
                    {
                        "group_id": "dup_1",
                        "match_kind": "ast-equivalent",
                        "items": [
                            {"path": "src/runtime/a.py", "symbol": "helper"},
                            {"path": "src/runtime/b.py", "symbol": "helper"},
                        ],
                    }
                ]
            }), encoding="utf-8")
            (reports / "symbol_reference_census.json").write_text(json.dumps({
                "items": [
                    {"path": "src/runtime/a.py", "symbol": "helper", "external_refs": 4, "role": "production-like"},
                    {"path": "src/runtime/b.py", "symbol": "helper", "external_refs": 1, "role": "production-like"},
                ]
            }), encoding="utf-8")

            subprocess.run(["python3", str(SCORER), "--run-root", str(run_root)], check=True, capture_output=True, text=True)
            payload = json.loads((reports / "candidate_score_report.json").read_text(encoding="utf-8"))

        duplicate = next(item for item in payload["items"] if item["candidate_type"] == "duplicate-symbol")
        self.assertEqual(duplicate["priority_band"], "high-probability-next")

    def test_candidate_scoring_promotes_strong_merge_back_support_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_root = tmp / "repo"
            repo_root.mkdir()
            run_root = tmp / "run" / "20260428T000000Z"
            reports = run_root / "reports"
            reports.mkdir(parents=True)
            (reports / "run_manifest.json").write_text(json.dumps({"repo_root": str(repo_root)}), encoding="utf-8")
            (reports / "support_split_census.json").write_text(json.dumps({
                "paths": [
                    {"path": "src/runtime/helper_support.py", "real_consumers": 1, "test_consumers": 0}
                ]
            }), encoding="utf-8")
            (reports / "single_consumer_census.json").write_text(json.dumps({
                "items": [
                    {"path": "src/runtime/helper_support.py", "consumer_count": 1}
                ]
            }), encoding="utf-8")
            (reports / "symbol_reference_census.json").write_text(json.dumps({
                "items": [
                    {"path": "src/runtime/helper_support.py", "symbol": "helper_support", "external_refs": 0}
                ]
            }), encoding="utf-8")
            (reports / "symbol_reachability_census.json").write_text(json.dumps({
                "symbols": [
                    {"path": "src/runtime/helper_support.py", "suspicion": "needs-proof"}
                ]
            }), encoding="utf-8")
            (reports / "fallback_exception_census.json").write_text(json.dumps({
                "findings": [
                    {"path": "src/runtime/helper_support.py", "fallback_keywords": ["normalize"]}
                ]
            }), encoding="utf-8")
            (reports / "production_path_proof.json").write_text(json.dumps({
                "items": [
                    {
                        "path": "src/runtime/helper_support.py",
                        "current_owner_confidence": "merge-back-candidate",
                        "caller_proof": {"production_importers": ["src/runtime/main.py"]},
                        "registration_sites": [],
                        "constructor_sites": [],
                    }
                ]
            }), encoding="utf-8")

            subprocess.run(["python3", str(SCORER), "--run-root", str(run_root)], check=True, capture_output=True, text=True)
            payload = json.loads((reports / "candidate_score_report.json").read_text(encoding="utf-8"))

        support_item = next(item for item in payload["items"] if item["path_or_group"] == "src/runtime/helper_support.py")
        self.assertEqual(support_item["priority_band"], "high-probability-next")


if __name__ == "__main__":
    unittest.main()
