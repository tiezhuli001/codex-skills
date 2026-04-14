#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from census_utils import classify_role, import_targets, iter_python_files, module_name, parse_python

CANDIDATE_KEYWORDS = (
    "support",
    "helper",
    "helpers",
    "adapter",
    "adapters",
    "util",
    "utils",
    "view",
    "views",
    "builder",
    "builders",
    "fixture",
    "fixtures",
    "mock",
    "mocks",
    "stub",
    "stubs",
    "compat",
    "wrapper",
    "wrappers",
    "alias",
    "aliases",
)


def is_candidate_path(root: Path, path: Path) -> bool:
    rel = str(path.relative_to(root)).lower()
    return any(keyword in rel for keyword in CANDIDATE_KEYWORDS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-consumers", type=int, default=1)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    py_files = iter_python_files(root)
    module_by_path = {path: module_name(root, path) for path in py_files}
    imports_by_path = {}
    for path in py_files:
        tree = parse_python(path)
        imports_by_path[path] = import_targets(tree) if tree is not None else set()

    items = []
    for path, mod in sorted(module_by_path.items(), key=lambda item: str(item[0])):
        if not mod:
            continue
        if not is_candidate_path(root, path):
            continue
        consumers = []
        for other, targets in imports_by_path.items():
            if other == path:
                continue
            if (
                mod in targets
                or any(target.startswith(mod + ".") for target in targets)
                or any(target.endswith("." + mod) for target in targets)
            ):
                consumers.append(str(other.relative_to(root)))
        if len(consumers) > args.max_consumers:
            continue
        role = classify_role(root, path)
        signals = []
        if len(consumers) == 0:
            signals.append("no-known-import-consumers")
        if len(consumers) == 1:
            signals.append("single-consumer-support-split")
        items.append(
            {
                "path": str(path.relative_to(root)),
                "role": role,
                "consumer_count": len(consumers),
                "consumers": consumers,
                "signals": signals or ["needs-proof"],
            }
        )

    payload = {
        "run_id": out.parent.parent.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "tool_name": "single_consumer_census",
        "schema_version": 1,
        "items": items,
    }
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
