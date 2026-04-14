#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from census_utils import classify_role, iter_python_files, name_tokens, parse_python


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-external-refs", type=int, default=2)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    py_files = iter_python_files(root)
    token_counters: dict[Path, Counter[str]] = {}
    trees: dict[Path, ast.AST] = {}
    for path in py_files:
        tree = parse_python(path)
        if tree is None:
            continue
        trees[path] = tree
        token_counters[path] = Counter(name_tokens(tree))

    items = []
    for path, tree in sorted(trees.items(), key=lambda item: str(item[0])):
        role = classify_role(root, path)
        for node in getattr(tree, "body", []):
            if isinstance(node, ast.FunctionDef):
                kind = "function"
            elif isinstance(node, ast.AsyncFunctionDef):
                kind = "async-function"
            elif isinstance(node, ast.ClassDef):
                kind = "class"
            else:
                continue
            symbol = node.name
            internal_refs = max(0, token_counters[path][symbol] - 1)
            consumer_files = []
            role_breakdown = Counter()
            external_refs = 0
            for other, counter in token_counters.items():
                if other == path:
                    continue
                count = counter[symbol]
                if count <= 0:
                    continue
                external_refs += count
                consumer_files.append(str(other.relative_to(root)))
                role_breakdown[classify_role(root, other)] += 1
            if external_refs > args.max_external_refs:
                continue
            signals = []
            if external_refs == 0:
                signals.append("no-external-references")
            if external_refs <= 2:
                signals.append("low-external-reference-count")
            items.append(
                {
                    "symbol": symbol,
                    "kind": kind,
                    "path": str(path.relative_to(root)),
                    "role": role,
                    "internal_refs": internal_refs,
                    "external_refs": external_refs,
                    "consumer_files": consumer_files,
                    "consumer_role_breakdown": dict(role_breakdown),
                    "signals": signals or ["needs-proof"],
                }
            )

    payload = {
        "run_id": out.parent.parent.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "tool_name": "symbol_reference_census",
        "schema_version": 1,
        "items": items,
    }
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
