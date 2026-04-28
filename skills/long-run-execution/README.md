# long-run-execution

Execution discipline for long-running Codex tasks that should continue through verified slices instead of collapsing into summaries, handoffs, or fake blockers.

## What it does

`long-run-execution` is for situations where the user wants the agent to keep going through verified slices instead of stopping at:
- analysis
- handoff notes
- midpoint summaries
- vague “next agent can continue” output
- asking the user for repo context that can be discovered locally

It pushes the agent toward:
- smallest executable frontier
- immediate verification after each slice
- continuity updates that reflect reality
- continued progress until the requested outcome is done or truly blocked
- explicit continue/stop decisions and anti-rationalization checks

## Design principles

- execution first
- verification before claims
- no fake stopping points
- no handoff-as-substitute-for-work
- keep scope tight and aligned to the current slice
- treat side issues as classify-and-return, not scope expansion
- stop only for real blockers with evidence

## Directory layout

```text
long-run-execution/
  SKILL.md
  execution-templates.md
  long-run-review-template.md
  pressure-corpus.md
  test-prompts.json
```

## Install

From the repo root:

```bash
./scripts/install.sh long-run-execution
```

## Best fit

Use this skill when the user clearly wants uninterrupted execution—“keep going”, “just do it”, “fix it fully”, “don’t stop at analysis”, or “continue until blocked”.
