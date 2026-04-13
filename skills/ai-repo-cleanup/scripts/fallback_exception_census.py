#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

EXCEPT_RE = re.compile(r"except\s+Exception")
KEYWORDS = ("fallback", "legacy", "compat", "alias", "normalize")


def main() -> int:
    run_root = Path(sys.argv[1])
    repo_root = Path.cwd()
    findings = []
    for base in (repo_root / "src", repo_root / "tests"):
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            broad = len(EXCEPT_RE.findall(text))
            kws = sorted({kw for kw in KEYWORDS if kw in text})
            if broad or kws:
                findings.append({
                    "path": str(path.relative_to(repo_root)),
                    "broad_exception_count": broad,
                    "fallback_keywords": kws,
                    "notes": "signal only; verify whether fallback is still required",
                })
    obj = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "fallback_exception_census",
        "schema_version": 1,
        "findings": findings,
    }
    out = run_root / "reports" / "fallback_exception_census.json"
    out.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
