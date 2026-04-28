#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from census_utils import read_run_manifest, resolve_repo_root


GENERIC_CLUSTER_NAME_TOKENS = {"family", "runtime", "test", "tests", "tool", "tools", "contract"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cross-score cleanup candidates from multiple ai-repo-cleanup reports.")
    parser.add_argument("--run-root", required=True, help="Run root created by prepare_tmp_workspace.py or run_full_audit.py")
    parser.add_argument("--repo-root", default=None, help="Target repository root override. Defaults to run_manifest repo_root, then cwd.")
    parser.add_argument("--out", default=None, help="Output JSON path. Defaults to <run_root>/reports/candidate_score_report.json")
    parser.add_argument("--max-high-priority", type=int, default=8, help="Maximum number of items kept in High-Probability Next.")
    return parser.parse_args()


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _priority_band(score: int, candidate_type: str) -> str:
    if candidate_type == "large-test-family" and score >= 85:
        return "high-probability-next"
    if candidate_type == "duplicate-symbol" and score >= 70:
        return "high-probability-next"
    if score >= 50:
        return "aggressive-backlog"
    return "hold"


def _name_tokens(label: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9]+", label.lower())
        if token not in GENERIC_CLUSTER_NAME_TOKENS and len(token) >= 4
    }


def _entry(
    path_or_group: str,
    candidate_type: str,
    score: int,
    evidence: list[str],
    missing_proof: list[str],
    next_check: str,
    action: str,
    source_reports: list[str],
    priority_band_override: str | None = None,
    **extra: object,
) -> dict:
    payload = {
        "path_or_group": path_or_group,
        "candidate_type": candidate_type,
        "score": score,
        "priority_band": priority_band_override or _priority_band(score, candidate_type),
        "key_evidence": evidence,
        "missing_proof": missing_proof,
        "fastest_next_check": next_check,
        "suggested_action": action,
        "source_reports": source_reports,
    }
    payload.update(extra)
    return payload


def _score_owner_cluster(cluster: dict) -> int:
    size = cluster.get("cluster_size", {})
    files = int(size.get("files", 0))
    lines = int(size.get("lines", 0))
    tests = int(size.get("tests", 0))
    overlap_count = len(cluster.get("overlap_tokens", []))

    score = 35
    if files >= 2:
        score += 10
    if files >= 3:
        score += 5
    if lines >= 1200:
        score += 20
    elif lines >= 600:
        score += 10
    if tests >= 30:
        score += 10
    elif tests >= 15:
        score += 5
    if overlap_count >= 6:
        score += 15
    elif overlap_count >= 3:
        score += 10
    elif overlap_count >= 1:
        score += 5
    if files <= 4 and overlap_count >= 6:
        score += 10
    if files >= 5 and overlap_count <= 1:
        score -= 10
    elif files >= 8 and overlap_count <= 2:
        score -= 15
    elif files >= 10 and overlap_count <= 3:
        score -= 10
    return max(score, 0)


def _cluster_files(cluster: dict) -> set[str]:
    return {row.get("path", "") for row in cluster.get("owner_map", []) if row.get("path")}


def _cluster_overlap_ratio(left: dict, right: dict) -> float:
    left_files = _cluster_files(left)
    right_files = _cluster_files(right)
    if not left_files or not right_files:
        return 0.0
    return len(left_files & right_files) / min(len(left_files), len(right_files))


def _should_merge_cluster(left: dict, right: dict) -> bool:
    overlap_ratio = _cluster_overlap_ratio(left, right)
    if overlap_ratio < 0.66:
        return False
    return bool(_name_tokens(left.get("path_or_group", "")) & _name_tokens(right.get("path_or_group", "")))


def _merge_owner_clusters(owner_clusters: list[dict]) -> list[dict]:
    if not owner_clusters:
        return []

    parent = {idx: idx for idx in range(len(owner_clusters))}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i, left in enumerate(owner_clusters):
        for j in range(i + 1, len(owner_clusters)):
            right = owner_clusters[j]
            if _should_merge_cluster(left, right):
                union(i, j)

    groups: dict[int, list[dict]] = {}
    for idx, cluster in enumerate(owner_clusters):
        groups.setdefault(find(idx), []).append(cluster)

    merged: list[dict] = []
    for members in groups.values():
        if len(members) == 1:
            cluster = dict(members[0])
            cluster["merged_from"] = [cluster.get("path_or_group", "unknown")]
            merged.append(cluster)
            continue

        owner_rows_by_path: dict[str, dict] = {}
        for member in members:
            for row in member.get("owner_map", []):
                path = row.get("path")
                if not path:
                    continue
                existing = owner_rows_by_path.get(path)
                if existing is None:
                    owner_rows_by_path[path] = dict(row)
                    continue
                existing["line_count"] = max(int(existing.get("line_count", 0)), int(row.get("line_count", 0)))
                existing["test_count"] = max(int(existing.get("test_count", 0)), int(row.get("test_count", 0)))
                dominant = list(dict.fromkeys([*existing.get("dominant_tokens", []), *row.get("dominant_tokens", [])]))
                existing["dominant_tokens"] = dominant[:6]

        primary = max(
            members,
            key=lambda item: (
                len(item.get("overlap_tokens", [])),
                int(item.get("cluster_size", {}).get("lines", 0)),
                -len(item.get("owner_map", [])),
            ),
        )
        owner_rows = sorted(owner_rows_by_path.values(), key=lambda row: row.get("path", ""))
        first_batch_exact_targets = list(
            dict.fromkeys(
                target
                for member in members
                for target in member.get("first_batch_exact_targets", [])
                if isinstance(target, str) and target
            )
        )[:6]
        if not first_batch_exact_targets:
            first_batch_exact_targets = [f"trim repeated assertions around {token}" for token in primary.get("overlap_tokens", [])[:3]]

        merged.append(
            {
                "path_or_group": primary.get("path_or_group", "unknown"),
                "candidate_type": "large-test-family-owner-map",
                "cluster_size": {
                    "files": len(owner_rows),
                    "lines": sum(int(row.get("line_count", 0)) for row in owner_rows),
                    "tests": sum(int(row.get("test_count", 0)) for row in owner_rows),
                },
                "current_round_maturity": primary.get("current_round_maturity", "mapping-first"),
                "overlap_tokens": sorted(
                    {
                        token
                        for member in members
                        for token in member.get("overlap_tokens", [])
                        if isinstance(token, str) and token
                    }
                )[:12],
                "owner_map": owner_rows,
                "first_batch_exact_targets": first_batch_exact_targets,
                "proof_blockers": ["owner-proof", "contract-proof"],
                "merged_from": [member.get("path_or_group", "unknown") for member in members],
            }
        )

    merged.sort(key=lambda item: (-int(item.get("cluster_size", {}).get("lines", 0)), item.get("path_or_group", "")))
    return merged


def _cluster_verification(cluster: dict) -> list[dict]:
    files = [row.get("path") for row in cluster.get("owner_map", []) if row.get("path")]
    owner_suite = files[0] if files else "<owner-suite>"
    regression_slice = " ".join(files[:2]) if len(files) >= 2 else owner_suite
    return [
        {
            "check_class": "owner tests",
            "purpose": "protect the likely owner slice while overlap assertions are trimmed",
            "proof": f"python3 -m pytest {owner_suite}",
            "pass_signal": "owner slice stays green",
        },
        {
            "check_class": "protected regression",
            "purpose": "catch cross-suite contract drift during the first deletion batch",
            "proof": f"python3 -m pytest {regression_slice}",
            "pass_signal": "protected regression stays green",
        },
    ]


def _cluster_action_targets(cluster: dict) -> list[str]:
    owner_rows = sorted(
        [row for row in cluster.get("owner_map", []) if row.get("path")],
        key=lambda row: (-int(row.get("line_count", 0)), row.get("path", "")),
    )
    overlap_tokens = cluster.get("overlap_tokens", [])
    inherited = [
        target
        for target in cluster.get("first_batch_exact_targets", [])
        if isinstance(target, str) and target
    ]
    if not owner_rows:
        return inherited

    targets: list[str] = []
    owners = [row.get("path", "") for row in owner_rows[:2] if row.get("path")]
    trim_from = [row.get("path", "") for row in owner_rows[2:4] if row.get("path")]
    if owners:
        targets.append(f"keep owner candidate coverage in {', '.join(owners)}")
    if trim_from:
        token = overlap_tokens[0] if overlap_tokens else "overlap"
        targets.append(f"trim repeated {token} assertions from {', '.join(trim_from)}")
    if owners and len(owner_rows) >= 2:
        token = overlap_tokens[0] if overlap_tokens else "shared"
        targets.append(f"verify the {token} slice stays protected across {', '.join(owners[:2])}")
    return list(dict.fromkeys([*targets, *inherited]))[:6]


def _symbol_ref_entry(symbol_ref_by_path: dict[str, list[dict]], path: str, symbol: str) -> dict:
    for item in symbol_ref_by_path.get(path, []):
        if item.get("symbol") == symbol:
            return item
    return {}


def _pick_canonical_owner(dup_items: list[dict], symbol_ref_by_path: dict[str, list[dict]]) -> dict:
    ranked: list[dict] = []
    for item in dup_items:
        path = item.get("path", "")
        symbol = item.get("symbol", "")
        ref = _symbol_ref_entry(symbol_ref_by_path, path, symbol)
        role = ref.get("role", "unknown")
        ranked.append(
            {
                "path": path,
                "symbol": symbol,
                "external_refs": int(ref.get("external_refs", 0)),
                "role": role,
                "sort_key": (
                    1 if role == "production-like" else 0,
                    int(ref.get("external_refs", 0)),
                    -path.count("/"),
                    -len(path),
                    path,
                ),
            }
        )
    if not ranked:
        return {}
    ranked.sort(key=lambda item: item["sort_key"], reverse=True)
    best = dict(ranked[0])
    best.pop("sort_key", None)
    return best


def _duplicate_verification(canonical_owner: dict) -> list[dict]:
    owner_path = canonical_owner.get("path", "<canonical-owner>")
    symbol = canonical_owner.get("symbol", "<symbol>")
    return [
        {
            "check_class": "caller proof",
            "purpose": "confirm only one canonical helper implementation remains after consolidation",
            "proof": f"rg -n \"{symbol}\" src tests",
            "pass_signal": f"one surviving owner remains at {owner_path} and callers reference that path only",
        }
    ]


def _support_verification(path: str) -> list[dict]:
    return [
        {
            "check_class": "execution-path regression",
            "purpose": "confirm the runtime path still uses the surviving owner seam",
            "proof": f"trace live callers for {path}",
            "pass_signal": "runtime ownership stays consistent",
        }
    ]


def _high_priority_sort_key(item: dict) -> tuple:
    type_bonus = {
        "duplicate-symbol": 4,
        "thin-wrapper": 3,
        "support-or-low-reference-candidate": 2,
        "large-test-family": 1,
    }.get(item.get("candidate_type", ""), 0)
    current_owner_confidence = item.get("current_owner_confidence")
    proof_bonus = 1 if current_owner_confidence == "merge-back-candidate" else 0
    return (
        type_bonus,
        proof_bonus,
        int(item.get("score", 0)),
        -len(item.get("cluster_files", [])),
        str(item.get("path_or_group", "")),
    )


def _apply_high_priority_cap(items: list[dict], max_high_priority: int) -> None:
    if max_high_priority <= 0:
        return
    high_indices = [idx for idx, item in enumerate(items) if item.get("priority_band") == "high-probability-next"]
    ranked_indices = sorted(high_indices, key=lambda idx: _high_priority_sort_key(items[idx]), reverse=True)
    keep = set(ranked_indices[:max_high_priority])
    for rank, idx in enumerate(ranked_indices, start=1):
        items[idx]["priority_rank"] = rank
        if idx in keep:
            continue
        items[idx]["priority_band"] = "aggressive-backlog"
        items[idx]["demoted_by_cap"] = True
        notes = items[idx].setdefault("key_evidence", [])
        notes.append(f"demoted_by_cap=top_{max_high_priority}")


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    repo_root = resolve_repo_root(run_root, args.repo_root)
    reports = run_root / "reports"
    out = Path(args.out).expanduser().resolve() if args.out else reports / "candidate_score_report.json"
    manifest = read_run_manifest(run_root)

    tests = _read_json(reports / "test_surface_census.json")
    owner_map = _read_json(reports / "test_owner_map.json")
    duplicates = _read_json(reports / "duplicate_symbol_census.json")
    thin_wrappers = _read_json(reports / "thin_wrapper_census.json")
    production_proof = _read_json(reports / "production_path_proof.json")
    support = _read_json(reports / "support_split_census.json")
    single = _read_json(reports / "single_consumer_census.json")
    symbol_ref = _read_json(reports / "symbol_reference_census.json")
    reachability = _read_json(reports / "symbol_reachability_census.json")
    fallback = _read_json(reports / "fallback_exception_census.json")

    support_by_path = {item.get("path", ""): item for item in support.get("paths", [])}
    single_by_path = {item.get("path", ""): item for item in single.get("items", [])}
    fallback_by_path = {item.get("path", ""): item for item in fallback.get("findings", [])}
    reachability_by_path: dict[str, list[dict]] = {}
    for item in reachability.get("symbols", []):
        reachability_by_path.setdefault(item.get("path", ""), []).append(item)
    symbol_ref_by_path: dict[str, list[dict]] = {}
    for item in symbol_ref.get("items", []):
        symbol_ref_by_path.setdefault(item.get("path", ""), []).append(item)

    proof_by_path = {item.get("path", ""): item for item in production_proof.get("items", [])}

    items: list[dict] = []

    owner_clusters = _merge_owner_clusters(owner_map.get("clusters", []))
    if owner_clusters:
        for cluster in owner_clusters:
            size = cluster.get("cluster_size", {})
            score = _score_owner_cluster(cluster)
            items.append(
                _entry(
                    cluster.get("path_or_group", "unknown"),
                    "large-test-family",
                    score,
                    [
                        f"file_count={size.get('files', 0)}",
                        f"line_count={size.get('lines', 0)}",
                        f"overlap_tokens={','.join(cluster.get('overlap_tokens', []))}",
                    ],
                    ["owner-proof", "contract-proof"],
                    "use the generated owner_map and first_batch_exact_targets to prune overlap",
                    cluster.get("current_round_maturity", "mapping-first"),
                    ["test_owner_map.json"],
                    cluster_files=sorted(_cluster_files(cluster)),
                    merged_from=cluster.get("merged_from", []),
                    first_batch_exact_targets=_cluster_action_targets(cluster),
                    verification_matrix=_cluster_verification(cluster),
                )
            )
    else:
        for family in tests.get("families", []):
            file_count = int(family.get("file_count", 0))
            line_count = int(family.get("line_count", 0))
            test_count = int(family.get("test_count", 0))
            if file_count < 3 and line_count < 1200:
                continue
            score = 45
            if file_count >= 3:
                score += 15
            if line_count >= 1200:
                score += 20
            if test_count >= 30:
                score += 10
            items.append(
                _entry(
                    family.get("path", "unknown"),
                    "large-test-family",
                    score,
                    [f"file_count={file_count}", f"line_count={line_count}", f"test_count={test_count}"],
                    ["owner-proof", "contract-proof"],
                    "build one owner map and exact deletion list for this family",
                    "mapping-first",
                    ["test_surface_census.json"],
                    cluster_files=[],
                    first_batch_exact_targets=[f"build first-batch deletion list for {family.get('path', 'unknown')}"],
                    verification_matrix=[],
                )
            )

    for group in duplicates.get("duplicate_groups", []):
        dup_items = group.get("items", [])
        label = ", ".join(f"{item.get('path')}::{item.get('symbol')}" for item in dup_items[:4])
        score = 70 + min(20, 5 * max(0, len(dup_items) - 1))
        canonical_owner = _pick_canonical_owner(dup_items, symbol_ref_by_path)
        items.append(
            _entry(
                label,
                "duplicate-symbol",
                score,
                [f"match_kind={group.get('match_kind', 'unknown')}", f"item_count={len(dup_items)}"],
                ["owner-proof", "contract-proof"],
                "compare callers and centralize on one canonical implementation",
                "proof-first",
                ["duplicate_symbol_census.json", "symbol_reference_census.json"],
                canonical_owner=canonical_owner,
                duplicate_paths=[item.get("path", "") for item in dup_items if item.get("path")],
                verification_matrix=_duplicate_verification(canonical_owner),
            )
        )

    for item in thin_wrappers.get("items", []):
        path = f"{item.get('path', 'unknown')}::{item.get('symbol', 'unknown')}"
        items.append(
            _entry(
                path,
                "thin-wrapper",
                55,
                [f"target_calls={','.join(item.get('target_calls', []))}", f"statement_count={item.get('statement_count', 0)}"],
                ["owner-proof", "caller-proof"],
                "check whether the only forwarded call can move into the canonical owner module",
                "proof-first",
                ["thin_wrapper_census.json"],
                verification_matrix=_support_verification(path),
            )
        )

    candidate_paths = set(support_by_path) | set(single_by_path) | set(symbol_ref_by_path) | set(reachability_by_path) | set(fallback_by_path)
    for path in sorted(candidate_paths):
        score = 0
        evidence: list[str] = []
        sources: list[str] = []
        item_support = support_by_path.get(path)
        if item_support:
            score += 20
            evidence.append(f"support_split real={item_support.get('real_consumers', 0)} test={item_support.get('test_consumers', 0)}")
            sources.append("support_split_census.json")
            if int(item_support.get("real_consumers", 0)) <= 1:
                score += 15
            if int(item_support.get("test_consumers", 0)) <= 1:
                score += 10
        item_single = single_by_path.get(path)
        if item_single:
            score += 20
            evidence.append(f"single_consumer={item_single.get('consumer_count', 0)}")
            sources.append("single_consumer_census.json")
        refs = symbol_ref_by_path.get(path, [])
        if refs:
            corroborated_refs = [ref for ref in refs if ref.get("external_refs", 99) <= 1]
            if corroborated_refs:
                score += 10
                evidence.append(f"low_reference_symbols={len(corroborated_refs)}")
                sources.append("symbol_reference_census.json")
        reach = reachability_by_path.get(path, [])
        if reach:
            if any(item.get("suspicion") in {"high-suspicion-dead", "needs-proof", "test-only-proof"} for item in reach):
                score += 10
                evidence.append("reachability-needs-proof")
                sources.append("symbol_reachability_census.json")
            if all(item.get("suspicion") == "do-not-touch-yet" for item in reach) and score < 40:
                continue
        item_fallback = fallback_by_path.get(path)
        if item_fallback:
            score += 10
            evidence.append(f"fallback_keywords={','.join(item_fallback.get('fallback_keywords', []))}")
            sources.append("fallback_exception_census.json")
        item_proof = proof_by_path.get(path)
        caller_proof = item_proof.get("caller_proof", {}) if item_proof else {}
        production_importers = caller_proof.get("production_importers", []) if isinstance(caller_proof, dict) else []
        if item_proof:
            evidence.append(f"owner_confidence={item_proof.get('current_owner_confidence', 'unknown')}")
            evidence.append(f"production_importers={len(production_importers)}")
            evidence.append(f"registration_sites={len(item_proof.get('registration_sites', []))}")
            evidence.append(f"constructor_sites={len(item_proof.get('constructor_sites', []))}")
            sources.append("production_path_proof.json")
            if item_proof.get("current_owner_confidence") == "merge-back-candidate":
                score += 10
            else:
                score += 5
        if score < 50:
            continue
        owner_confidence = item_proof.get("current_owner_confidence", "unknown") if item_proof else "unknown"
        priority_override = None
        if owner_confidence == "merge-back-candidate" and score >= 95:
            priority_override = "high-probability-next"
        items.append(
            _entry(
                path,
                "support-or-low-reference-candidate",
                score,
                evidence,
                ["runtime-proof", "owner-proof"],
                "trace runtime ownership and challenge only if corroborating signals still hold",
                "proof-first",
                sorted(set(sources)),
                priority_band_override=priority_override,
                current_owner_confidence=owner_confidence,
                production_importers=sorted(set(production_importers)),
                registration_sites=item_proof.get("registration_sites", []) if item_proof else [],
                constructor_sites=item_proof.get("constructor_sites", []) if item_proof else [],
                verification_matrix=_support_verification(path),
            )
        )

    items.sort(key=lambda item: (-int(item.get("score", 0)), str(item.get("path_or_group", ""))))
    _apply_high_priority_cap(items, args.max_high_priority)
    payload = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "score_cleanup_candidates",
        "schema_version": 1,
        "audit_scope": manifest.get("audit_scope", "repo-scan"),
        "max_high_priority": args.max_high_priority,
        "items": items,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
