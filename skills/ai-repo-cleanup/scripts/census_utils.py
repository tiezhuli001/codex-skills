#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import shutil
import subprocess
from pathlib import Path

ROLE_KEYWORDS = {
    "production-like": ("src", "app", "apps", "service", "services", "runtime", "core", "server", "client"),
    "test-like": ("test", "tests", "spec", "fixture", "mock", "stub"),
    "docs-like": ("docs", "design", "plan", "audit", "review", "adr", "changelog", "status", "handoff"),
    "generated-or-vendor": (
        "node_modules",
        ".venv",
        "vendor",
        "dist",
        "build",
        "coverage",
        ".pytest_cache",
        "__pycache__",
        ".next",
        "target",
        "out",
    ),
}


def iter_tracked_files(root: Path) -> list[Path] | None:
    if not (root / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        path = root / line
        if path.is_file():
            paths.append(path)
    return sorted(paths)


def iter_repo_files(root: Path) -> list[Path]:
    tracked = iter_tracked_files(root)
    if tracked is not None:
        return tracked
    return [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts
    ]


def iter_python_files(root: Path) -> list[Path]:
    return [path for path in iter_repo_files(root) if path.suffix == ".py"]


def classify_role(root: Path, path: Path) -> str:
    rel = path.relative_to(root)
    parts = tuple(part.lower() for part in rel.parts)
    for role in ("generated-or-vendor", "test-like", "docs-like", "production-like"):
        keywords = ROLE_KEYWORDS[role]
        if any(keyword == part or keyword in part for part in parts for keyword in keywords):
            return role
    if path.suffix.lower() in {".md", ".rst", ".adoc", ".txt"}:
        return "docs-like"
    if path.suffix.lower() == ".py":
        return "production-like"
    return "unknown-or-mixed"


def module_name(root: Path, path: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    parts = list(rel.parts)
    if parts and parts[0] in {"src"}:
        parts = parts[1:]
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def parse_python(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return None


def import_targets(tree: ast.AST) -> set[str]:
    targets: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                targets.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module:
                targets.add(module)
                for alias in node.names:
                    targets.add(f"{module}.{alias.name}")
    return targets


def name_tokens(tree: ast.AST) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.Attribute):
            names.append(node.attr)
    return names


def read_run_manifest(run_root: Path) -> dict:
    manifest = run_root / "reports" / "run_manifest.json"
    if not manifest.exists():
        return {}
    try:
        return json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def resolve_repo_root(run_root: Path, explicit_repo_root: str | None = None) -> Path:
    if explicit_repo_root:
        return Path(explicit_repo_root).expanduser().resolve()
    payload = read_run_manifest(run_root)
    repo_root = payload.get("repo_root")
    if isinstance(repo_root, str) and repo_root.strip():
        return Path(repo_root).expanduser().resolve()
    return Path.cwd().resolve()


def externalize_paths(repo_root: Path, run_root: Path, relative_paths: list[str]) -> list[dict[str, str]]:
    artifacts_dir = run_root / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    moved: list[dict[str, str]] = []
    for raw in relative_paths:
        src = repo_root / raw
        if not src.exists():
            continue
        dst = artifacts_dir / src.name
        if dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        shutil.move(str(src), str(dst))
        moved.append({"from": str(src.relative_to(repo_root)), "to": str(dst)})
    return moved
