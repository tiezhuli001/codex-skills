#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path


ROLE_NAMES = (
    "production-like",
    "test-like",
    "docs-like",
    "generated-or-vendor",
    "unknown-or-mixed",
)

PATH_KEYWORDS = {
    "production-like": (
        "src",
        "app",
        "apps",
        "config",
        "script",
        "scripts",
        "bin",
        "lib",
        "pkg",
        "cmd",
        "service",
        "services",
        "runtime",
        "core",
        "server",
        "client",
        "backend",
        "frontend",
    ),
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
DOC_FILENAMES = ("readme", "changelog", "status", "handoff", "adr")
PRODUCTION_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".rb",
    ".php",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
}
DOC_EXTENSIONS = {".md", ".rst", ".adoc", ".txt"}
TEXT_EXTENSIONS = PRODUCTION_EXTENSIONS | DOC_EXTENSIONS | {".json", ".toml", ".yaml", ".yml", ".sh", ".data"}
COMMENT_PREFIXES = {
    ".py": ("#",),
    ".sh": ("#",),
    ".rb": ("#",),
    ".yml": ("#",),
    ".yaml": ("#",),
    ".toml": ("#",),
    ".js": ("//",),
    ".ts": ("//",),
    ".tsx": ("//",),
    ".jsx": ("//",),
    ".java": ("//",),
    ".c": ("//",),
    ".cc": ("//",),
    ".cpp": ("//",),
    ".h": ("//",),
    ".hpp": ("//",),
    ".go": ("//",),
    ".rs": ("//",),
    ".php": ("//", "#"),
}
TEST_PATTERNS = (
    re.compile(r"(^|/)(test_[^/]+|[^/]+_test\.[^/]+|[^/]+\.spec\.[^/]+|[^/]+\.test\.[^/]+)$"),
)
TEST_CONTENT_HINTS = ("pytest", "unittest", "describe(", "it(", "expect(", "self.assert")
DOC_CONTENT_HINTS = ("# ", "## ", "### ", "- ", "* ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--top-n", type=int, default=5)
    parser.add_argument("--include-generated", action="store_true")
    return parser.parse_args()


def is_text_path(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS or path.suffix == ""


def iter_tracked_files(root: Path):
    git_dir = root / ".git"
    if not git_dir.exists():
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
    paths = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        candidate = root / line
        if candidate.is_file():
            paths.append(candidate)
    return sorted(paths)


def iter_files(root: Path):
    tracked = iter_tracked_files(root)
    if tracked is not None:
        yield from tracked
        return
    for path in sorted(root.rglob("*")):
        if path.is_file():
            yield path


def path_parts_lower(relpath: str) -> tuple[str, ...]:
    return tuple(part.lower() for part in Path(relpath).parts)


def classify_file(root: Path, path: Path) -> tuple[str, dict[str, int], list[str], str]:
    relpath = str(path.relative_to(root))
    rel_lower = relpath.lower()
    parts = path_parts_lower(relpath)
    scores = defaultdict(int)
    notes: list[str] = []

    generated_hit = False
    for role, keywords in PATH_KEYWORDS.items():
        for keyword in keywords:
            if any(keyword == part or keyword in part for part in parts):
                scores[role] += 2
                notes.append(f"path:{role}:{keyword}")
                if role == "generated-or-vendor":
                    generated_hit = True
                break

    for pattern in TEST_PATTERNS:
        if pattern.search(rel_lower):
            scores["test-like"] += 3
            notes.append("filename:test-pattern")
            break

    stem_lower = path.stem.lower()
    if any(stem_lower.startswith(name) for name in DOC_FILENAMES):
        scores["docs-like"] += 3
        notes.append("filename:docs-name")

    suffix = path.suffix.lower()
    if suffix in PRODUCTION_EXTENSIONS:
        scores["production-like"] += 2
        notes.append(f"extension:production:{suffix}")
    if suffix in DOC_EXTENSIONS:
        scores["docs-like"] += 2
        notes.append(f"extension:docs:{suffix}")

    text = ""
    if is_text_path(path):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            text = ""

    if text:
        lowered = text.lower()
        if any(hint in lowered for hint in TEST_CONTENT_HINTS):
            scores["test-like"] += 2
            notes.append("content:test-hint")
        if suffix in DOC_EXTENSIONS or sum(lowered.count(h) for h in DOC_CONTENT_HINTS) >= 2:
            scores["docs-like"] += 2
            notes.append("content:docs-hint")

    if generated_hit:
        scores["generated-or-vendor"] += 3
        notes.append("priority:generated-path")

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    if not ranked:
        return "unknown-or-mixed", scores, notes, relpath
    if ranked[0][1] <= 0:
        return "unknown-or-mixed", scores, notes, relpath
    if len(ranked) > 1 and ranked[0][1] - ranked[1][1] <= 1:
        return "unknown-or-mixed", scores, notes, relpath
    return ranked[0][0], scores, notes, relpath


def line_metrics(path: Path) -> tuple[int, int, int]:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return 0, 0, 0
    total = len(lines)
    non_empty = 0
    non_comment = 0
    comment_prefixes = COMMENT_PREFIXES.get(path.suffix.lower(), ())
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        non_empty += 1
        if comment_prefixes and any(stripped.startswith(prefix) for prefix in comment_prefixes):
            continue
        non_comment += 1
    return total, non_empty, non_comment


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    out = Path(args.out).resolve()
    roles = {
        role: {
            "files": 0,
            "total_lines": 0,
            "non_empty_lines": 0,
            "non_empty_non_comment_lines": 0,
        }
        for role in ROLE_NAMES
    }
    top_paths: dict[str, list[dict[str, object]]] = {role: [] for role in ROLE_NAMES}
    classification_notes: list[dict[str, object]] = []
    scanned_files = 0

    for path in iter_files(root):
        scanned_files += 1
        role, scores, notes, relpath = classify_file(root, path)
        total, non_empty, non_comment = line_metrics(path)

        if role == "generated-or-vendor" and not args.include_generated:
            # still count in role totals; only interpretation changes upstream
            pass

        roles[role]["files"] += 1
        roles[role]["total_lines"] += total
        roles[role]["non_empty_lines"] += non_empty
        roles[role]["non_empty_non_comment_lines"] += non_comment
        top_paths[role].append(
            {
                "path": relpath,
                "non_empty_lines": non_empty,
                "notes": notes[:3],
            }
        )
        if role == "unknown-or-mixed":
            classification_notes.append(
                {
                    "path": relpath,
                    "scores": {key: value for key, value in scores.items() if value > 0},
                    "notes": notes,
                }
            )

    for role in ROLE_NAMES:
        top_paths[role] = sorted(
            top_paths[role],
            key=lambda item: int(item["non_empty_lines"]),
            reverse=True,
        )[: args.top_n]

    production_non_empty = roles["production-like"]["non_empty_lines"]
    test_non_empty = roles["test-like"]["non_empty_lines"]
    docs_non_empty = roles["docs-like"]["non_empty_lines"]
    payload = {
        "summary": {
            "scanned_files": scanned_files,
            "classified_files": scanned_files - roles["unknown-or-mixed"]["files"],
            "unknown_files": roles["unknown-or-mixed"]["files"],
        },
        "roles": roles,
        "derived_signals": {
            "largest_role_by_non_empty_lines": max(
                ROLE_NAMES,
                key=lambda role: roles[role]["non_empty_lines"],
            ),
            "test_like_to_production_like_ratio": round(test_non_empty / production_non_empty, 3)
            if production_non_empty
            else None,
            "docs_like_to_production_like_ratio": round(docs_non_empty / production_non_empty, 3)
            if production_non_empty
            else None,
        },
        "top_paths": top_paths,
        "classification_notes": classification_notes[: args.top_n],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
