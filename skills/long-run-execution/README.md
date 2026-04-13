# long-run-execution

Execution discipline for long-running Codex tasks.

## What it does

`long-run-execution` is for situations where the user wants the agent to keep going through verified slices instead of stopping at:
- analysis
- handoff notes
- midpoint summaries
- vague “next agent can continue” output

It pushes the agent toward:
- smallest executable frontier
- immediate verification after each slice
- continuity updates that reflect reality
- continued progress until the requested outcome is done or truly blocked

## Design principles

- execution first
- verification before claims
- no fake stopping points
- no handoff-as-substitute-for-work
- keep scope tight and aligned to the current slice

## Directory layout

```text
long-run-execution/
  SKILL.md
  long-run-review-template.md
```

## Install

From the repo root:

```bash
./scripts/install.sh long-run-execution
```

## Best fit

Use this skill when the user clearly wants uninterrupted execution to the next verified milestone.
