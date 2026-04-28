#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from census_utils import resolve_repo_root

EXCEPT_RE = re.compile(r"except\s+Exception")
KEYWORDS = ("fallback", "legacy", "compat", "alias", "normalize")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find broad exception handlers and fallback-heavy files as cleanup signals.")
    parser.add_argument("run_root", help="Run root created by prepare_tmp_workspace.py")
    parser.add_argument("--repo-root", default=None, help="Target repository root. Defaults to run_manifest repo_root, then cwd.")
    parser.add_argument("--out", default=None, help="Output JSON path. Defaults to <run_root>/reports/fallback_exception_census.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    repo_root = resolve_repo_root(run_root, args.repo_root)
    findings = []
    for base in (repo_root / "src", repo_root / "tests"):
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            broad = len(EXCEPT_RE.findall(text))
            kws = sorted({kw for kw in KEYWORDS if kw in text})
            if broad or kws:
                findings.append(
                    {
                        "path": str(path.relative_to(repo_root)),
                        "broad_exception_count": broad,
                        "fallback_keywords": kws,
                        "notes": "signal only; verify whether fallback is still required",
                    }
                )
    obj = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "fallback_exception_census",
        "schema_version": 1,
        "findings": findings,
    }
    out = Path(args.out).expanduser().resolve() if args.out else run_root / "reports" / "fallback_exception_census.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
