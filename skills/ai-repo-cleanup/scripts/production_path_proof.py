#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from census_utils import import_targets, iter_python_files, module_name, parse_python, resolve_repo_root

REGISTRATION_HINTS = ("register", "bootstrap", "catalog", "route", "binding", "discover")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gather caller, constructor, and registration proof for production cleanup candidates.")
    parser.add_argument("--run-root", required=True, help="Run root created by prepare_tmp_workspace.py or run_full_audit.py")
    parser.add_argument("--repo-root", default=None, help="Target repository root override. Defaults to run_manifest repo_root, then cwd.")
    parser.add_argument("--out", default=None, help="Output JSON path. Defaults to <run_root>/reports/production_path_proof.json")
    return parser.parse_args()


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _exported_symbols(tree: ast.AST | None) -> list[str]:
    if tree is None:
        return []
    names = []
    for node in getattr(tree, "body", []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not node.name.startswith("_"):
            names.append(node.name)
    return names


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    repo_root = resolve_repo_root(run_root, args.repo_root)
    out = Path(args.out).expanduser().resolve() if args.out else run_root / "reports" / "production_path_proof.json"
    reports = run_root / "reports"
    support = _read_json(reports / "support_split_census.json")
    single = _read_json(reports / "single_consumer_census.json")

    candidate_paths = sorted(
        {
            item.get("path", "")
            for item in support.get("paths", []) + single.get("items", [])
            if isinstance(item.get("path"), str) and item.get("path")
        }
    )

    py_files = iter_python_files(repo_root)
    imports_by_path = {}
    text_by_path = {}
    tree_by_path = {}
    for path in py_files:
        tree = parse_python(path)
        tree_by_path[path] = tree
        imports_by_path[path] = import_targets(tree) if tree is not None else set()
        text_by_path[path] = path.read_text(encoding="utf-8", errors="ignore")

    items = []
    tests_root = repo_root / "tests"
    for rel in candidate_paths:
        candidate_path = repo_root / rel
        if not candidate_path.exists():
            continue
        tree = tree_by_path.get(candidate_path) or parse_python(candidate_path)
        exported = _exported_symbols(tree)
        mod = module_name(repo_root, candidate_path)
        production_importers = []
        test_importers = []
        registration_sites = []
        constructor_sites = []
        for other in py_files:
            if other == candidate_path:
                continue
            imports = imports_by_path.get(other, set())
            text = text_by_path.get(other, "")
            if mod in imports or any(target.startswith(mod + ".") for target in imports):
                rel_other = str(other.relative_to(repo_root))
                if tests_root.exists() and other.is_relative_to(tests_root):
                    test_importers.append(rel_other)
                else:
                    production_importers.append(rel_other)
                    lowered = text.lower()
                    if any(hint in lowered for hint in REGISTRATION_HINTS):
                        registration_sites.append(rel_other)
                    if any(re.search(rf"\b{re.escape(symbol)}\s*\(", text) for symbol in exported):
                        constructor_sites.append(rel_other)
        confidence = "merge-back-candidate"
        if registration_sites or len(production_importers) > 1:
            confidence = "live-boundary"
        items.append(
            {
                "path": rel,
                "module_name": mod,
                "exported_symbols": exported,
                "caller_proof": {
                    "production_importers": sorted(set(production_importers)),
                    "test_importers": sorted(set(test_importers)),
                },
                "registration_sites": sorted(set(registration_sites)),
                "constructor_sites": sorted(set(constructor_sites)),
                "current_owner_confidence": confidence,
                "proof_summary": [
                    f"production_importers={len(set(production_importers))}",
                    f"registration_sites={len(set(registration_sites))}",
                    f"constructor_sites={len(set(constructor_sites))}",
                ],
            }
        )

    payload = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "production_path_proof",
        "schema_version": 1,
        "items": items,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
