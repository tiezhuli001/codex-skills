# ai-repo-cleanup

A deletion-oriented cleanup audit for AI / agent repositories that surfaces delete-ready items, high-probability next candidates, and aggressive backlog items a coding agent can act on.

## What it does

`ai-repo-cleanup` is built to challenge repository surface before edits and turn the result into an execution package:
- dead code suspicion
- duplicate implementation or duplicate intent
- wrappers, adapters, helper/support seams, and single-consumer splits
- compat or legacy residue
- false-alive paths and tests
- non-core surface growth that outpaces the active spine

It is intentionally aggressive in candidate discovery and conservative only in final deletion claims.

## Output style

A good run should produce:
- one repo-level execution package
- compact candidate entries with evidence, surviving contract, missing proof, fastest next check, and suggested action
- module execution sheets only for current-round actionable items
- zero-action compression when no meaningful cleanup action exists

## Design principles

- maximize candidate discovery before verdict compression
- runtime and producer evidence outrank graph and code-shape hints
- missing proof must be named instead of hidden
- optional tools must not pollute the repo
- GitNexus and symbol tools may help analysis, but must not generate or rewrite repository instruction files
- if no delete-ready, high-probability, or meaningful backlog item exists, the output must stay short

## Directory layout

```text
ai-repo-cleanup/
  SKILL.md
  references/
  scripts/
  tests/
  test-prompts.json
```

## Install

From the repo root:

```bash
./scripts/install.sh ai-repo-cleanup
```

## Notes

This skill is most useful before a coding agent starts a cleanup round, when you want a deletion-oriented audit that already names the next proof and next action instead of stopping at broad analysis.
