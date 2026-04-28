from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
RENDER = SKILL_ROOT / "scripts" / "render_cleanup_package.py"


class RenderCleanupPackageTests(unittest.TestCase):
    def test_render_cleanup_package_help_exits_cleanly(self) -> None:
        completed = subprocess.run(
            ["python3", str(RENDER), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("usage", completed.stdout.lower())

    def test_render_cleanup_package_builds_markdown_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            run_root = tmp / "run" / "20260428T000000Z"
            reports = run_root / "reports"
            reports.mkdir(parents=True)
            repo_root = tmp / "repo"
            repo_root.mkdir()
            (repo_root / "requirements.txt").write_text("pytest\n", encoding="utf-8")
            (reports / "run_manifest.json").write_text(json.dumps({
                "run_id": run_root.name,
                "repo_root": str(repo_root),
                "audit_scope": "repo-scan",
                "tool_name": "run_full_audit",
                "schema_version": 1,
            }), encoding="utf-8")
            (reports / "repo_surface.json").write_text(json.dumps({
                "repo_root": str(repo_root),
                "tool_name": "repo_surface_snapshot",
                "schema_version": 1,
                "summary": {"scanned_files": 10, "classified_files": 9, "unknown_files": 1},
                "roles": {
                    "production-like": {"files": 3, "total_lines": 120, "non_empty_lines": 100, "non_empty_non_comment_lines": 95},
                    "test-like": {"files": 4, "total_lines": 260, "non_empty_lines": 220, "non_empty_non_comment_lines": 210},
                    "docs-like": {"files": 2, "total_lines": 80, "non_empty_lines": 70, "non_empty_non_comment_lines": 65},
                    "generated-or-vendor": {"files": 0, "total_lines": 0, "non_empty_lines": 0, "non_empty_non_comment_lines": 0},
                    "unknown-or-mixed": {"files": 1, "total_lines": 5, "non_empty_lines": 5, "non_empty_non_comment_lines": 5},
                },
            }), encoding="utf-8")
            (reports / "test_surface_census.json").write_text(json.dumps({
                "repo_root": str(repo_root),
                "tool_name": "test_surface_census",
                "schema_version": 1,
                "families": [
                    {"path": "tests/runtime_loop", "file_count": 4, "line_count": 1500, "test_count": 40},
                    {"path": "tests/feishu", "file_count": 3, "line_count": 900, "test_count": 25},
                ],
            }), encoding="utf-8")
            (reports / "duplicate_symbol_census.json").write_text(json.dumps({
                "repo_root": str(repo_root),
                "tool_name": "duplicate_symbol_census",
                "schema_version": 1,
                "duplicate_groups": [
                    {
                        "group_id": "dup_1",
                        "match_kind": "ast-equivalent",
                        "items": [
                            {"path": "src/runtime/a.py", "symbol": "helper"},
                            {"path": "src/runtime/b.py", "symbol": "helper"},
                        ],
                        "signals": ["duplicate-implementation"],
                    }
                ],
            }), encoding="utf-8")
            (reports / "support_split_census.json").write_text(json.dumps({
                "repo_root": str(repo_root),
                "tool_name": "support_split_census",
                "schema_version": 1,
                "paths": [
                    {"path": "src/runtime/helper_support.py", "kind": "helper_support", "real_consumers": 1, "test_consumers": 1, "notes": "candidate only"}
                ],
            }), encoding="utf-8")
            (reports / "single_consumer_census.json").write_text(json.dumps({
                "repo_root": str(repo_root),
                "tool_name": "single_consumer_census",
                "schema_version": 1,
                "items": [
                    {"path": "src/runtime/helper_support.py", "role": "production-like", "consumer_count": 1, "consumers": ["src/runtime/main.py"], "signals": ["single-consumer-support-split"]}
                ],
            }), encoding="utf-8")
            (reports / "complexity_budget_census.json").write_text(json.dumps({
                "repo_root": str(repo_root),
                "tool_name": "complexity_budget_census",
                "schema_version": 1,
                "files": [
                    {"path": "src/runtime/loop.py", "line_count": 800, "function_count": 20, "branch_like_count": 50, "broad_exception_count": 1}
                ],
            }), encoding="utf-8")
            (reports / "fallback_exception_census.json").write_text(json.dumps({
                "repo_root": str(repo_root),
                "tool_name": "fallback_exception_census",
                "schema_version": 1,
                "findings": [
                    {"path": "src/runtime/legacy.py", "broad_exception_count": 1, "fallback_keywords": ["legacy"], "notes": "signal only"}
                ],
            }), encoding="utf-8")
            (reports / "candidate_score_report.json").write_text(json.dumps({
                "items": [
                    {
                        "path_or_group": "contract-gateway-message family",
                        "candidate_type": "large-test-family",
                        "score": 99,
                        "priority_band": "high-probability-next",
                        "key_evidence": ["file_count=3", "line_count=1500", "overlap_tokens=card,session,message"],
                        "missing_proof": ["owner-proof", "contract-proof"],
                        "fastest_next_check": "use the generated owner_map and first_batch_exact_targets to prune overlap",
                        "suggested_action": "mapping-first",
                        "cluster_files": [
                            "tests/test_gateway.py",
                            "tests/contracts/test_gateway_contracts.py",
                            "tests/contracts/test_runtime_contracts.py",
                        ],
                        "first_batch_exact_targets": [
                            "trim duplicate final-card assertions from contract suite",
                            "keep endpoint state-flow assertions in gateway suite",
                        ],
                        "verification_matrix": [
                            {
                                "check_class": "owner tests",
                                "purpose": "protect the gateway owner slice",
                                "proof": "python3 -m pytest tests/test_gateway.py",
                                "pass_signal": "gateway owner suite stays green",
                            }
                        ],
                    },
                    {
                        "path_or_group": "src/runtime/a.py::helper, src/runtime/b.py::helper",
                        "candidate_type": "duplicate-symbol",
                        "score": 88,
                        "priority_band": "high-probability-next",
                        "key_evidence": ["match_kind=ast-equivalent", "item_count=2"],
                        "missing_proof": ["owner-proof", "contract-proof"],
                        "fastest_next_check": "compare callers and centralize on one canonical implementation",
                        "suggested_action": "proof-first",
                        "canonical_owner": {
                            "path": "src/runtime/a.py",
                            "symbol": "helper",
                            "external_refs": 4,
                        },
                        "verification_matrix": [
                            {
                                "check_class": "protected regression",
                                "purpose": "keep runtime helper behavior stable",
                                "proof": "python3 -m pytest tests/test_runtime.py",
                                "pass_signal": "runtime helper regression stays green",
                            }
                        ],
                    },
                ]
            }), encoding="utf-8")
            (reports / "wave_stability_report.json").write_text(json.dumps({
                "status": "compared",
                "previous_run_id": "20260427T010101Z",
                "current_run_id": "20260428T000000Z",
                "new_candidates": [{"path_or_group": "contract-gateway-message family", "candidate_type": "large-test-family"}],
                "promoted_candidates": [{"path_or_group": "src/runtime/a.py::helper, src/runtime/b.py::helper", "candidate_type": "duplicate-symbol"}],
                "resolved_candidates": [],
                "persistent_candidates": [{"path_or_group": "src/runtime/helper_support.py", "candidate_type": "support-or-low-reference-candidate"}],
            }), encoding="utf-8")

            subprocess.run(["python3", str(RENDER), "--run-root", str(run_root)], check=True, capture_output=True, text=True)
            text = (reports / "cleanup_execution_package.md").read_text(encoding="utf-8")

        self.assertIn("## Delete-Ready Now", text)
        self.assertIn("## High-Probability Next", text)
        self.assertIn("## Aggressive Candidate Backlog", text)
        self.assertIn("## Current-Wave Action Board", text)
        self.assertIn("## Wave Stability", text)
        self.assertIn("contract-gateway-message family", text)
        self.assertIn("trim duplicate final-card assertions from contract suite", text)
        self.assertIn("python3 -m pytest tests/test_gateway.py", text)
        self.assertIn("src/runtime/a.py::helper", text)
        self.assertIn("preferred canonical owner", text)
        self.assertIn("20260427T010101Z", text)
        self.assertIn("## Cleanup Execution Package", text)
