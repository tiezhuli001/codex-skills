# Candidate Census Design

Use this reference when extending repo-cleanup scripts.

Goal: improve **candidate discovery** without turning scripts into deletion judges.

## Principles

- Keep script behavior generic across runtime code, support code, tests, docs, and tooling.
- Prefer stable JSON over smart prose.
- Emit signals, counts, and weak evidence; let the skill do verdict compression.
- Use only system `python3` and lightweight parsing by default.
- Do not import the target repository's runtime code.

## Recommended Census Types

### symbol_reference_census
Find top-level symbols with weak external usage.

Useful fields:
- `symbol`
- `kind`
- `path`
- `role`
- `internal_refs`
- `external_refs`
- `consumer_files[]`
- `consumer_role_breakdown`
- `signals[]`

### duplicate_symbol_census
Find duplicate implementations or duplicate intent.

Useful fields:
- `group_id`
- `match_kind`
- `items[]`
  - `path`
  - `symbol`
  - `kind`
- `signals[]`

### thin_wrapper_census
Find functions whose main job is forwarding to another symbol.

Useful fields:
- `path`
- `symbol`
- `kind`
- `target_calls[]`
- `statement_count`
- `signals[]`

### single_consumer_census
Find files or modules with weak ownership.

Useful fields:
- `path`
- `role`
- `consumer_count`
- `consumers[]`
- `signals[]`

## Output Discipline

Scripts should say things like:
- `low-external-reference-count`
- `duplicate-implementation`
- `thin-wrapper`
- `single-consumer-support-split`
- `role-concentrated`
- `needs-proof`

Scripts should not say things like:
- `safe-to-delete`
- `must-remove`
- `dead-code-confirmed`

## Default Output Location

Write reports under:
`/tmp/skill/ai-repo-cleanup/runs/<timestamp>/reports/`

## Integration Rule

The skill should merge census outputs into:
- `delete-ready now`
- `high-probability next`
- `aggressive candidate backlog`
- `not-a-cleanup-priority`

Large backlog is acceptable when signals are explicit and proof gaps are named.
