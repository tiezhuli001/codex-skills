#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter
from datetime import datetime, timezone
from math import ceil
from pathlib import Path

from census_utils import resolve_repo_root


TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_]+")
STOPWORDS = {"test", "tests", "keep", "keeps", "returns", "return", "with", "without", "into", "from", "that"}
GENERIC_PATH_TOKENS = {
    "test",
    "tests",
    "runtime",
    "tool",
    "tools",
    "self",
    "main",
    "agent",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build owner-map candidates for large overlapping test families.")
    parser.add_argument("--run-root", required=True, help="Run root created by prepare_tmp_workspace.py or run_full_audit.py")
    parser.add_argument("--repo-root", default=None, help="Target repository root override. Defaults to run_manifest repo_root, then cwd.")
    parser.add_argument("--out", default=None, help="Output JSON path. Defaults to <run_root>/reports/test_owner_map.json")
    return parser.parse_args()


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="ignore").splitlines())


def _split_tokens(raw: str) -> list[str]:
    parts: list[str] = []
    for token in TOKEN_RE.findall(raw):
        for piece in token.split("_"):
            if not piece:
                continue
            lowered = piece.lower()
            if lowered.endswith("ies") and len(lowered) > 4:
                lowered = lowered[:-3] + "y"
            elif lowered.endswith("s") and not lowered.endswith("ss") and len(lowered) > 5:
                lowered = lowered[:-1]
            parts.append(lowered)
    return parts


def _extract_tokens(path: Path) -> tuple[list[str], int]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    tokens: list[str] = []
    test_count = 0
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ([tok for tok in tokens if tok not in STOPWORDS], test_count)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            test_count += 1
            tokens.extend(_split_tokens(node.name))
    return ([tok for tok in tokens if tok not in STOPWORDS and len(tok) >= 4], test_count)


def _extract_path_tokens(repo_root: Path, path: Path) -> list[str]:
    relative = path.relative_to(repo_root)
    tokens: list[str] = []
    for part in relative.parts:
        tokens.extend(_split_tokens(part))
    return [
        token
        for token in tokens
        if token not in STOPWORDS and token not in GENERIC_PATH_TOKENS and len(token) >= 4
    ]


def _cluster_name(counter: Counter[str], path_counter: Counter[str]) -> str:
    top: list[str] = []
    for token, count in path_counter.most_common():
        if count >= 2:
            top.append(token)
        if len(top) >= 2:
            break
    for token, _ in counter.most_common():
        if token in top:
            continue
        top.append(token)
        if len(top) >= 3:
            break
    if not top:
        return "test-family"
    return "-".join(top) + " family"


def _top_overlap_tokens(rows: list[dict], corpus_df: Counter[str]) -> list[str]:
    threshold = max(2, ceil(len(rows) * 0.5))
    counter: Counter[str] = Counter()
    for row in rows:
        counter.update(set(row["content_tokens"]))
    ranked = [
        token
        for token, count in counter.most_common()
        if count >= threshold and corpus_df[token] <= max(12, threshold * 3)
    ]
    return ranked[:12]


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    repo_root = resolve_repo_root(run_root, args.repo_root)
    out = Path(args.out).expanduser().resolve() if args.out else run_root / "reports" / "test_owner_map.json"
    tests_root = repo_root / "tests"

    file_rows = []
    path_df: Counter[str] = Counter()
    content_df: Counter[str] = Counter()
    if tests_root.exists():
        for path in sorted(tests_root.rglob("test*.py")):
            content_tokens, test_count = _extract_tokens(path)
            path_tokens = _extract_path_tokens(repo_root, path)
            if not content_tokens and not path_tokens:
                continue
            content_df.update(set(content_tokens))
            path_df.update(set(path_tokens))
            file_rows.append(
                {
                    "path": str(path.relative_to(repo_root)),
                    "line_count": _line_count(path),
                    "content_tokens": content_tokens,
                    "content_token_counts": Counter(content_tokens),
                    "path_tokens": path_tokens,
                    "test_count": test_count,
                }
            )

    clusters = []
    max_seed_df = max(4, min(12, len(file_rows)))
    seen_file_sets: set[tuple[str, ...]] = set()
    for seed, df in sorted(path_df.items()):
        if df < 2 or df > max_seed_df:
            continue
        rows = [row for row in file_rows if seed in row["path_tokens"]]
        if len(rows) < 2:
            continue
        file_key = tuple(sorted(row["path"] for row in rows))
        if file_key in seen_file_sets:
            continue
        seen_file_sets.add(file_key)
        token_counter: Counter[str] = Counter()
        path_counter: Counter[str] = Counter()
        for row in rows:
            token_counter.update(row["content_token_counts"])
            path_counter.update(row["path_tokens"])
        overlap_tokens = _top_overlap_tokens(rows, content_df)
        if not overlap_tokens:
            overlap_tokens = [seed]
        owner_map = []
        total_lines = 0
        total_tests = 0
        for row in rows:
            dominant_tokens = [token for token, _ in row["content_token_counts"].most_common(4)]
            test_count = row["test_count"]
            total_lines += row["line_count"]
            total_tests += test_count
            owner_map.append(
                {
                    "path": row["path"],
                    "line_count": row["line_count"],
                    "dominant_tokens": dominant_tokens,
                    "test_count": test_count,
                }
            )
        clusters.append(
            {
                "path_or_group": _cluster_name(token_counter, path_counter),
                "candidate_type": "large-test-family-owner-map",
                "cluster_size": {"files": len(rows), "lines": total_lines, "tests": total_tests},
                "current_round_maturity": "mapping-first",
                "overlap_tokens": sorted(overlap_tokens),
                "owner_map": owner_map,
                "first_batch_exact_targets": [f"review overlap around {token}" for token in sorted(overlap_tokens)[:3]],
                "proof_blockers": ["owner-proof", "contract-proof"],
            }
        )

    clusters.sort(key=lambda item: (-item["cluster_size"]["lines"], item["path_or_group"]))
    payload = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "test_owner_map",
        "schema_version": 1,
        "clusters": clusters,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
