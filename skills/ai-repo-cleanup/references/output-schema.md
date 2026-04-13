# AI Repo Cleanup Output Schema

All stable script outputs should default to JSON files under:
`/tmp/skill/ai-repo-cleanup/runs/<timestamp>/reports/`

## Common fields
Every JSON file should include when practical:
- `run_id`
- `generated_at`
- `repo_root`
- `tool_name`
- `schema_version`

## Suggested report files
- `run_manifest.json`
- `repo_scan_snapshot.json`
- `test_surface_census.json`
- `support_split_census.json`
- `symbol_reachability_census.json`
- `fallback_exception_census.json`
- `complexity_budget_census.json`
- `gitnexus_snapshot.json`
- `artifact_externalization.json`

## Schema hints
### run_manifest.json
- `delivery_mode`
- `audit_scope`
- `execution_goal`
- `artifacts_externalized`
- `delete_ready_count`
- `high_probability_count`
- `later_phase_count`
- `cleanup_worthy_modules[]`

### repo_scan_snapshot.json
- `git_status`
- `diff_stat`
- `top_changed_files`
- `top_test_files`
- `notes`

### test_surface_census.json
- `families[]`
  - `path`
  - `file_count`
  - `line_count`
  - `test_count`

### support_split_census.json
- `paths[]`
  - `path`
  - `kind`
  - `real_consumers`
  - `test_consumers`
  - `notes`

### symbol_reachability_census.json
- `symbols[]`
  - `name`
  - `path`
  - `kind`
  - `reference_count`
  - `test_reference_count`
  - `production_reference_count`
  - `suspicion`

### fallback_exception_census.json
- `findings[]`
  - `path`
  - `broad_exception_count`
  - `fallback_keywords`
  - `notes`

### complexity_budget_census.json
- `files[]`
  - `path`
  - `line_count`
  - `function_count`
  - `branch_like_count`
  - `broad_exception_count`

Scripts should prefer omission over unstable inference.
