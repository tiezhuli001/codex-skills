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
- `repo_surface.json`
- `single_consumer_census.json`
- `symbol_reference_census.json`
- `duplicate_symbol_census.json`
- `thin_wrapper_census.json`
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
- `single_live_checklist`
- `delete_ready_count`
- `high_probability_count`
- `aggressive_backlog_count`
- `expected_residual_count`
- `cleanup_worthy_modules[]`

### repo_scan_snapshot.json
- `git_status`
- `diff_stat`
- `top_changed_files`
- `notes`

### repo_surface.json
- `roles`
- `ratios`
- `top_paths_by_role`
- `classification_notes`

### single_consumer_census.json
- `items[]`
  - `path`
  - `role`
  - `consumer_count`
  - `consumers[]`
  - `signals[]`

### symbol_reference_census.json
- `items[]`
  - `symbol`
  - `kind`
  - `path`
  - `role`
  - `internal_refs`
  - `external_refs`
  - `consumer_files[]`
  - `consumer_role_breakdown`
  - `signals[]`

### duplicate_symbol_census.json
- `duplicate_groups[]`
  - `group_id`
  - `match_kind`
  - `items[]`
  - `signals[]`

### thin_wrapper_census.json
- `items[]`
  - `path`
  - `symbol`
  - `kind`
  - `target_calls[]`
  - `statement_count`
  - `signals[]`

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

## Checklist-friendly fields

When a script emits grouped cleanup candidates, prefer these fields:
- `path_or_group`
- `candidate_type`
- `key_evidence[]`
- `surviving_contract[]`
- `missing_proof[]`
- `fastest_next_check`
- `suggested_action`

For large grouped candidates, also include:
- `cluster_size`
- `current_round_maturity`
- `first_batch_exact_targets[]`
- `expected_immediate_deletions`
- `proof_blockers[]`

For execution packaging, also include:
- `ordered_actions[]`
- `verification_matrix[]`
  - `check_class`
  - `purpose`
  - `command_or_proof`
  - `pass_signal`
- `churn_expectation`
  - `expected_code_delta`
  - `expected_test_delta`
  - `expected_docs_delta`
  - `expected_net_line_direction`
- `expected_residuals[]`
  - `path_or_group`
  - `why_it_remains`
  - `future_unlock`

Scripts should prefer omission over unstable inference.
