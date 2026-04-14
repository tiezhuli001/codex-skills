# Repository Surface Snapshot

Use this reference to capture a lightweight size snapshot that helps order a repo cleanup audit.

The snapshot is an **audit-ordering signal**.

It is **not** a deletion verdict.

## When to Read This

Read this file when:
- the repository is large enough that audit ordering matters
- directory conventions are unclear
- the repo is mixed-language
- tests or docs appear larger than the active spine
- fixed directory assumptions would obviously be wrong

If the repo is small and role split is obvious, a lightweight in-turn classification is enough.

## Default Roles

Classify files by **role**, not fixed directories.

Roles:
- `production-like`
- `test-like`
- `docs-like`
- `generated-or-vendor`
- `unknown-or-mixed`

### production-like
Runtime, product, library, app, service, operator, or CLI implementation files.

### test-like
Tests, fixtures, mocks, replay cases, fake servers, and test-only support files.

### docs-like
README, design docs, plans, audits, reviews, ADRs, changelogs, handoff, and status docs.

### generated-or-vendor
Vendored, generated, cached, built, or compiled artifacts. Exclude these from the primary slimming baseline unless the user explicitly wants them audited.

### unknown-or-mixed
Use when signals conflict or classification is unclear. Prefer this over forced guessing.

## Classification Signals

Use multiple weak signals together.

### Path signals
Examples:
- test-like: `test`, `tests`, `spec`, `fixture`, `mock`, `stub`
- docs-like: `docs`, `design`, `plan`, `audit`, `review`, `adr`, `changelog`, `status`, `handoff`
- generated-or-vendor: `node_modules`, `.venv`, `vendor`, `dist`, `build`, `coverage`, `.pytest_cache`, `__pycache__`, `.next`, `target`, `out`

### Filename signals
Examples:
- test-like: `test_*`, `*_test.*`, `*.spec.*`, `*.test.*`
- docs-like: `README*`, `CHANGELOG*`, `STATUS*`, `HANDOFF*`, `ADR*`

### Extension signals
Examples:
- production-like: `.py`, `.js`, `.ts`, `.tsx`, `.jsx`, `.go`, `.rs`, `.java`, `.kt`, `.rb`, `.php`, `.c`, `.cc`, `.cpp`, `.h`, `.hpp`
- docs-like: `.md`, `.rst`, `.adoc`, `.txt`

### Content signals
Use lightweight hints only:
- test-like: test framework imports, assertion-heavy structure, `describe(`, `it(`, `expect(`
- docs-like: heading density, prose-heavy structure
- generated-or-vendor: minified or obviously generated content
- production-like: runtime/service/module structure without test-framework dominance

## Suggested Strategy

Use a lightweight score model.

Example:
- path signal: `+2`
- filename signal: `+3`
- extension signal: `+2`
- content signal: `+2`
- conflicting signal: `-2`

If one role clearly wins, classify to that role.

If top roles are too close, use `unknown-or-mixed`.

## Counting Rules

For each file, collect when practical:
- `total_lines`
- `non_empty_lines`
- `non_empty_non_comment_lines`

Use best-effort comment stripping only. Do not build a full parser.

If comment detection is uncertain, keep `non_empty_lines` accurate and treat non-comment counts as heuristic.

## Output Shape

A stable JSON output should include:
- summary counts
- per-role file and line totals
- derived ratios such as:
  - `test-like / production-like`
  - `docs-like / production-like`
- top paths by role
- classification notes when confidence is weak

## How To Use In The Cleanup Output

Good uses:
- explain which role deserves earlier audit attention
- explain whether test/docs growth sits outside the active spine
- justify why test narrowing or docs review should move earlier or stay later

Bad uses:
- deleting the largest role first
- calling tests bloated from size alone
- archiving docs from size alone

## Guardrails

Do not let snapshot data overrule:
- reachability
- producer evidence
- caller evidence
- owner-test survival
- contract-preservation reasoning

Large surface means “inspect earlier,” not “delete now.”

## Recommended Script Contract

If implemented as a script:
- use only system `python3`
- avoid importing repo runtime code
- emit stable JSON
- write outputs outside the repo by default
- prefer `/tmp/skill/ai-repo-cleanup/runs/<timestamp>/...`

Suggested script:
- `scripts/repo_surface_snapshot.py`

Suggested CLI:
```bash
python3 scripts/repo_surface_snapshot.py --root . --out /tmp/.../repo-surface.json
```

## Fallback

If no script exists:
- use shell or lightweight one-off logic
- produce a reduced snapshot
- record weak-confidence areas

Missing snapshot tooling must not block the audit.
