# ai-repo-cleanup

Deletion-oriented repository slimming audit for AI / agent repositories.

## What it does

`ai-repo-cleanup` is built to help an agent find repository weight that is actually worth removing:
- dead code suspicion
- false-alive tests
- weak helper/support splits
- redundant support surfaces
- archive/doc noise that should not dominate the active repo

The output is meant to be an **execution package**, not a vague audit report.

## Output style

A good run should produce:
- one repo-level execution package
- module execution sheets only for current-round actionable items
- zero-action compression when no real cleanup action exists

## Design principles

- optimize for safe deletion value
- runtime and producer evidence outrank graph hints
- optional tools must not pollute the repo
- GitNexus may help analysis, but must not generate or rewrite repository instruction files
- if no delete-ready or high-probability item exists, the output must stay short

## Directory layout

```text
ai-repo-cleanup/
  SKILL.md
  references/
  scripts/
```

## Install

From the repo root:

```bash
./scripts/install.sh ai-repo-cleanup
```

## Notes

This skill is especially useful before a coding agent starts a cleanup round, not after the edits are already underway.
