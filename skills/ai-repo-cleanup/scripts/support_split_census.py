#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from census_utils import resolve_repo_root

PATTERN = re.compile(r"(support|helper|helpers|view|adapter|util|utils)")


def module_name(path: Path, repo_root: Path) -> str:
    rel = path.relative_to(repo_root / "src").with_suffix("")
    return ".".join(rel.parts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Census support/helper split candidates and count real versus test consumers.")
    parser.add_argument("run_root", help="Run root created by prepare_tmp_workspace.py")
    parser.add_argument("--repo-root", default=None, help="Target repository root. Defaults to run_manifest repo_root, then cwd.")
    parser.add_argument("--out", default=None, help="Output JSON path. Defaults to <run_root>/reports/support_split_census.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    repo_root = resolve_repo_root(run_root, args.repo_root)
    src_root = repo_root / "src"
    tests_root = repo_root / "tests"
    py_files = list(src_root.rglob("*.py")) if src_root.exists() else []
    test_files = list(tests_root.rglob("*.py")) if tests_root.exists() else []
    texts = {path: path.read_text(encoding="utf-8", errors="ignore") for path in py_files + test_files}
    rows = []
    for path in sorted(py_files):
        if not PATTERN.search(path.name):
            continue
        mod = module_name(path, repo_root)
        real = 0
        test = 0
        for other, text in texts.items():
            if other == path:
                continue
            if mod in text:
                if other.is_relative_to(tests_root):
                    test += 1
                else:
                    real += 1
        rows.append({
            "path": str(path.relative_to(repo_root)),
            "kind": path.stem,
            "real_consumers": real,
            "test_consumers": test,
            "notes": "candidate only; verify ownership before deletion",
        })
    obj = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "support_split_census",
        "schema_version": 1,
        "paths": rows,
    }
    out = Path(args.out).expanduser().resolve() if args.out else run_root / "reports" / "support_split_census.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
