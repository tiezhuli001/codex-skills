#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from census_utils import read_run_manifest, resolve_repo_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render one markdown cleanup execution package from an ai-repo-cleanup run_root.")
    parser.add_argument("--run-root", required=True, help="Run root created by prepare_tmp_workspace.py or run_full_audit.py")
    parser.add_argument("--repo-root", default=None, help="Target repository root override. Defaults to run_manifest repo_root, then cwd.")
    parser.add_argument("--out", default=None, help="Output markdown path. Defaults to <run_root>/reports/cleanup_execution_package.md")
    return parser.parse_args()


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _detect_test_command(repo_root: Path) -> str:
    if (repo_root / "pyproject.toml").exists() or (repo_root / "requirements.txt").exists():
        return "python3 -m pytest"
    if (repo_root / "package.json").exists():
        return "npm test --"
    if (repo_root / "go.mod").exists():
        return "go test ./..."
    return "repo-native test command"


def _format_candidate(item: dict) -> str:
    evidence_text = "; ".join(item.get("key_evidence", [])) if item.get("key_evidence") else "needs more evidence"
    lines = [
        f"- `path-or-group`: `{item.get('path_or_group', 'unknown')}`",
        f"  - `candidate-type`: `{item.get('candidate_type', 'unknown')}`",
        f"  - `key-evidence`: {evidence_text}",
        "  - `surviving-contract`: preserve one justified surviving owner contract",
        f"  - `missing-proof`: {', '.join(item.get('missing_proof', [])) or 'needs-proof'}",
        f"  - `fastest-next-check`: {item.get('fastest_next_check', 'needs more proof')}",
        f"  - `suggested-action`: `{item.get('suggested_action', 'needs-proof')}`",
    ]
    canonical_owner = item.get("canonical_owner", {})
    if canonical_owner:
        lines.append(
            "  - `preferred canonical owner`: "
            f"`{canonical_owner.get('path', 'unknown')}::{canonical_owner.get('symbol', 'unknown')}` "
            f"(external_refs={canonical_owner.get('external_refs', 0)})"
        )
    return "\n".join(lines)


def _fallback_candidates(tests: dict, duplicates: dict, support: dict, single: dict, fallback: dict) -> tuple[list[dict], list[dict]]:
    high_probability_entries: list[dict] = []
    backlog_entries: list[dict] = []

    families = sorted(tests.get("families", []), key=lambda item: item.get("line_count", 0), reverse=True)
    for family in families[:3]:
        if family.get("line_count", 0) < 800 and family.get("file_count", 0) < 3:
            continue
        high_probability_entries.append(
            {
                "path_or_group": family.get("path", "unknown"),
                "candidate_type": "large test family",
                "key_evidence": [
                    f"line_count={family.get('line_count', 0)}",
                    f"file_count={family.get('file_count', 0)}",
                    f"test_count={family.get('test_count', 0)}",
                ],
                "missing_proof": ["owner-proof", "contract-proof"],
                "fastest_next_check": "build one owner map and first-batch deletion list for this family",
                "suggested_action": "mapping-first",
            }
        )

    for group in duplicates.get("duplicate_groups", [])[:3]:
        items = group.get("items", [])
        label = ", ".join(f"{item.get('path')}::{item.get('symbol')}" for item in items[:4])
        high_probability_entries.append(
            {
                "path_or_group": label,
                "candidate_type": "duplicate symbol",
                "key_evidence": [
                    f"match_kind={group.get('match_kind', 'unknown')}",
                    f"item_count={len(items)}",
                ],
                "missing_proof": ["owner-proof", "contract-proof"],
                "fastest_next_check": "diff callers and centralize on one owner implementation",
                "suggested_action": "proof-first",
            }
        )

    for item in support.get("paths", [])[:4]:
        backlog_entries.append(
            {
                "path_or_group": item.get("path", "unknown"),
                "candidate_type": "support split / helper seam",
                "key_evidence": [
                    f"real_consumers={item.get('real_consumers', 0)}",
                    f"test_consumers={item.get('test_consumers', 0)}",
                ],
                "missing_proof": ["runtime-proof", "owner-proof"],
                "fastest_next_check": "trace construction path and decide merge-back versus keep-as-boundary",
                "suggested_action": "proof-first",
            }
        )

    for item in single.get("items", [])[:4]:
        backlog_entries.append(
            {
                "path_or_group": item.get("path", "unknown"),
                "candidate_type": "single-consumer candidate",
                "key_evidence": [
                    f"consumer_count={item.get('consumer_count', 0)}",
                    f"signals={','.join(item.get('signals', []))}",
                ],
                "missing_proof": ["caller-proof", "owner-proof"],
                "fastest_next_check": "verify whether the consumer can absorb this helper without losing clarity",
                "suggested_action": "proof-first",
            }
        )

    for item in fallback.get("findings", [])[:2]:
        backlog_entries.append(
            {
                "path_or_group": item.get("path", "unknown"),
                "candidate_type": "fallback-heavy file",
                "key_evidence": [
                    f"broad_exception_count={item.get('broad_exception_count', 0)}",
                    f"keywords={','.join(item.get('fallback_keywords', []))}",
                ],
                "missing_proof": ["runtime-proof", "contract-proof"],
                "fastest_next_check": "inspect whether fallback branches still match current provider or compatibility surface",
                "suggested_action": "needs-proof",
            }
        )

    return high_probability_entries, backlog_entries


def _render_action_board(items: list[dict]) -> str:
    if not items:
        return "- no focused current-wave action item surfaced\n"
    sections: list[str] = []
    for index, item in enumerate(items, start=1):
        lines = [f"### Action {index} — `{item.get('path_or_group', 'unknown')}`"]
        cluster_files = item.get("cluster_files", [])
        if cluster_files:
            lines.append(f"- candidate files: `{', '.join(cluster_files[:6])}`")
        canonical_owner = item.get("canonical_owner", {})
        if canonical_owner:
            lines.append(
                f"- preferred canonical owner: `{canonical_owner.get('path', 'unknown')}::{canonical_owner.get('symbol', 'unknown')}`"
            )
        targets = item.get("first_batch_exact_targets", [])
        if targets:
            lines.append("- first batch exact targets:")
            for target in targets[:4]:
                lines.append(f"  - {target}")
        verification = item.get("verification_matrix", [])
        if verification:
            lines.append("- candidate verification:")
            for check in verification[:4]:
                lines.append(
                    "  - "
                    f"`{check.get('check_class', 'check')}` — {check.get('purpose', 'verify the surviving slice')} | "
                    f"`{check.get('proof', 'repo-native proof')}` | {check.get('pass_signal', 'stays green')}"
                )
        sections.append("\n".join(lines))
    return "\n\n".join(sections) + "\n"


def _render_wave_stability(wave_stability: dict) -> str:
    status = wave_stability.get("status", "unavailable")
    if status == "no-previous-run":
        return "- previous comparable wave: `none`\n- current wave starts the stability baseline for this repository\n"
    if status != "compared":
        return "- wave stability report unavailable for this run\n"
    new_candidates = wave_stability.get("new_candidates", [])
    promoted_candidates = wave_stability.get("promoted_candidates", [])
    resolved_candidates = wave_stability.get("resolved_candidates", [])
    persistent_candidates = wave_stability.get("persistent_candidates", [])
    lines = [
        f"- previous run: `{wave_stability.get('previous_run_id', 'unknown')}`",
        f"- current run: `{wave_stability.get('current_run_id', 'unknown')}`",
        f"- new candidates: `{len(new_candidates)}`",
        f"- promoted candidates: `{len(promoted_candidates)}`",
        f"- resolved candidates: `{len(resolved_candidates)}`",
        f"- persistent candidates: `{len(persistent_candidates)}`",
    ]
    if new_candidates:
        lines.append(f"- newest candidate: `{new_candidates[0].get('path_or_group', 'unknown')}`")
    if promoted_candidates:
        lines.append(f"- promoted candidate: `{promoted_candidates[0].get('path_or_group', 'unknown')}`")
    if resolved_candidates:
        lines.append(f"- resolved candidate: `{resolved_candidates[0].get('path_or_group', 'unknown')}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    repo_root = resolve_repo_root(run_root, args.repo_root)
    reports = run_root / "reports"
    out = Path(args.out).expanduser().resolve() if args.out else reports / "cleanup_execution_package.md"

    manifest = read_run_manifest(run_root)
    surface = _read_json(reports / "repo_surface.json")
    tests = _read_json(reports / "test_surface_census.json")
    duplicates = _read_json(reports / "duplicate_symbol_census.json")
    support = _read_json(reports / "support_split_census.json")
    single = _read_json(reports / "single_consumer_census.json")
    complexity = _read_json(reports / "complexity_budget_census.json")
    fallback = _read_json(reports / "fallback_exception_census.json")
    scored = _read_json(reports / "candidate_score_report.json")
    wave_stability = _read_json(reports / "wave_stability_report.json")

    roles = surface.get("roles", {})
    prod = roles.get("production-like", {})
    test = roles.get("test-like", {})
    docs = roles.get("docs-like", {})
    summary = surface.get("summary", {})
    complexity_files = sorted(complexity.get("files", []), key=lambda item: item.get("line_count", 0), reverse=True)
    test_cmd = _detect_test_command(repo_root)

    delete_ready_entries: list[dict] = []
    high_probability_entries: list[dict] = []
    backlog_entries: list[dict] = []

    scored_items = scored.get("items", [])
    if scored_items:
        for item in scored_items:
            if item.get("priority_band") == "high-probability-next":
                high_probability_entries.append(item)
            elif item.get("priority_band") == "aggressive-backlog":
                backlog_entries.append(item)
    else:
        high_probability_entries, backlog_entries = _fallback_candidates(tests, duplicates, support, single, fallback)

    expected_residual_rows: list[tuple[str, str, str]] = []
    for item in complexity_files[:4]:
        expected_residual_rows.append(
            (
                item.get("path", "unknown"),
                f"high complexity hotspot remains after this round (`line_count={item.get('line_count', 0)}`, `branch_like_count={item.get('branch_like_count', 0)}`)",
                "owner-map or design work before cleanup-first edits",
            )
        )

    not_priority_rows = [
        ("docs/ and archive surfaces", "test and runtime-candidate cleanup have higher immediate execution value"),
        ("largest runtime core files", "these files sit on the active spine and need design-led changes"),
    ]

    text = f"""# AI Repo Cleanup Execution Package

## Scan Summary
- **Mode:** `{manifest.get('audit_scope', 'repo-scan')}`
- **Audit status:** `completed-for-this-round`
- **Delivery mode:** `{manifest.get('delivery_mode', 'cleanup-execution-handoff')}`
- **Repository type:** `AI / agent / runtime harness`
- **Run root:** `{run_root}`
- **Final checklist path:** `{out}`
- **In-repo output requested?:** `no`
- **Tool artifacts externalized?:** `yes`
- **Single live checklist for this wave?:** `yes`

## Audit Context
- **Audit scope for this run:** repo surface, test family density, duplicate symbols, support splits, single-consumer seams, fallback signals, complexity hotspots.
- **Primary evidence sources used:** `run_manifest.json`, `repo_surface.json`, `test_surface_census.json`, `duplicate_symbol_census.json`, `support_split_census.json`, `single_consumer_census.json`, `complexity_budget_census.json`, `fallback_exception_census.json`, `candidate_score_report.json`, and `wave_stability_report.json` when present.
- **What this audit intentionally did not prove:** live runtime ownership and exact deletion safety for large grouped candidates.

## Repository Goal And Active Spine
- **Repository goal / project target:** delete or merge back low-value layers while protecting the active runtime chain.
- **Runtime / execution model:** inferred from repository surface and run manifest.
- **Active spine:** `channel -> binding -> runtime loop -> builtin tool / MCP / skill -> delivery / diagnostics` when applicable.
- **Current growth hotspots:** production-like `{prod.get('files', 0)} files / {prod.get('total_lines', 0)} lines`; test-like `{test.get('files', 0)} files / {test.get('total_lines', 0)} lines`; docs-like `{docs.get('files', 0)} files / {docs.get('total_lines', 0)} lines`; scanned files `{summary.get('scanned_files', 0)}`.

## Delete-Ready Now
"""
    text += "\n".join(_format_candidate(item) for item in delete_ready_entries) if delete_ready_entries else "- no delete-ready item at current proof depth\n"
    text += "\n\n## High-Probability Next\n"
    text += "\n\n".join(_format_candidate(item) for item in high_probability_entries) if high_probability_entries else "- no high-probability candidate surfaced\n"
    text += "\n\n## Aggressive Candidate Backlog\n"
    text += "\n\n".join(_format_candidate(item) for item in backlog_entries) if backlog_entries else "- no backlog candidate surfaced\n"
    text += "\n\n## Current-Wave Action Board\n"
    text += _render_action_board(high_probability_entries)
    text += "\n## Wave Stability\n"
    text += _render_wave_stability(wave_stability)
    text += "\n## Expected Residuals\n| Path or group | Why it remains after this round | What unlocks it later |\n|---|---|---|\n"
    for path_or_group, why_it_remains, future_unlock in expected_residual_rows:
        text += f"| `{path_or_group}` | {why_it_remains} | {future_unlock} |\n"
    text += "\n## Not-a-Cleanup-Priority\n| Path or group | Why it stays out of scope this round |\n|---|---|\n"
    for path_or_group, reason in not_priority_rows:
        text += f"| `{path_or_group}` | {reason} |\n"
    text += f"""\n## Cleanup Execution Package

### Scope
- **Execution outcome for this round:** `actionable-cleanup`
- **Execution goal for the coding agent:** reduce grouped test overlap first, then validate production helper duplication and support seams.
- **How to use this package:** execute in order; reopen analysis only if proof fails or verification fails.

### Ordered Actions
1. Execute the current-wave action board from top to bottom.
2. Keep duplicate helper consolidation on the preferred canonical owner path.
3. Challenge support-split and single-consumer seams only after runtime ownership proof.

### Verification Matrix
| Check class | Purpose | Fastest command or proof | Pass signal |
|---|---|---|---|
| `owner tests` | protect the surviving suite after each deletion batch | `{test_cmd} <owner-suite>` | owner suite stays green |
| `protected regression` | catch main-chain spillover | `{test_cmd} <protected-regression-slice>` | protected regression stays green |
| `execution-path regression` | keep active request/delivery path safe | `repo-native request or runtime smoke` | active chain still boots and answers |
| `end-to-end smoke` | prove the live chain still works when the repo has one | `repo-native end-to-end smoke` | one complete end-to-end pass |
| `docs and hygiene checks` | keep the run portable and repo-relative | `help output + schema fields + repo-relative persisted docs` | reports stay portable and structured |

### Churn Expectation
- **Expected code delta:** `20-120` lines
- **Expected test delta:** `200-800` lines
- **Expected docs delta:** `20-120` lines
- **Expected net line direction:** `down`

### Stop Conditions
- proof fails
- verification fails
- runtime evidence conflicts with the checklist
- grouped candidate maturity is lower than expected after first proof
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
