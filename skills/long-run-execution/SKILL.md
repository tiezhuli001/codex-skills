---
name: long-run-execution
description: Use when a task spans multiple milestones and the user wants uninterrupted execution to the next verified outcome, such as “keep going”, “just do it”, “fix it fully”, “don’t stop at analysis”, “don’t give me a handoff”, or “continue until blocked”
---

# Long-Run Execution

## Overview

Use this when the user wants sustained execution to a verified outcome.

Stop only when one of these is true:

- the requested outcome is complete and verified
- the next slice is blocked by a real blocker
- a destructive or high-risk action needs explicit confirmation

Typical triggers: “继续做，别停”, “直接做，不要计划”, “修到通过为止”, “不要停在分析”, “keep going”, “just do it”, “continue until blocked”.

## Hard Rules

- Execute the next slice now when it is executable now.
- Keep execution in the main thread; do not replace it with handoff language.
- Do not end a turn with “I’ll do X next” when X is executable now.
- Do not ask for repo context that can be discovered locally.
- Keep docs work aligned with the active slice; do not let it replace implementation already in scope.
- Keep side issues classified as block, log, or defer; return to the active slice immediately.
- Treat delegated output as partial input; the main thread owns merge, fallback proof, and final done judgment.
- Re-run affected proof when proof context changed.
- Return to fixing when a check fails.

## Continue / Stop Ladder

Check in this order:

1. Is there a smallest useful slice that can be executed now?  
   - yes → execute it
2. Is the next slice blocked by a real blocker?  
   - yes → stop with blocker evidence
3. Is the next action destructive or high-risk?  
   - yes → ask for confirmation
4. Did the user explicitly ask to pause, review, or change direction?  
   - yes → stop
5. Otherwise → keep going

If you cannot name the next slice in one sentence, reduce scope until you can.

## Goal Lock

Keep three things stable inside each slice:

1. `Target outcome`
2. `Boundary`
3. `Proof`

Realign before editing more when current work no longer serves one of them.

## Execution Loop

For each slice:

1. Read the source of truth first:
   - prompt
   - relevant docs / plan / spec
   - primary continuity file
2. If the task has multiple acceptance items, extract a compact completion ledger: `item | proof | status`.
3. Lock the smallest useful executable frontier.
4. Execute only work that advances that frontier.
5. Run slice proof immediately.
6. Re-check alignment against goal, boundary, baseline docs, and invariants.
7. Sync the continuity file and any drifted plan / checklist / entry docs.
8. Continue to the next executable slice.

Status values for the ledger: `todo`, `doing`, `done`, `blocked`.

Use `execution-templates.md` only when the task needs explicit structure.

## Verification

Verification is the pacing mechanism for long tasks.

- Decide the slice proof before editing.
- For larger tasks, define a proof ladder: `slice proof`, `milestone proof`, `final proof`.
- Lock the proof context that matters: workspace or branch, target runtime or service, data or config source, artifact path.
- After each slice, run the narrowest relevant check.
- After each milestone, run the broader regression that matches the risk.
- Before ending the turn, run the strongest practical final check for the claimed state.

When waiting for an external signal:

- wait only if that signal is itself the current proof step
- set a bounded observation window and bounded retries first
- if the bound is hit, switch to another executable slice or stop with a blocker packet

## Delegation

Use subagents for bounded, independent work:

- targeted exploration
- isolated verification
- disjoint implementation chunks

The main thread still owns:

- the active boundary
- the completion ledger
- result merge
- fallback proof when a delegated result is incomplete or failed
- the final done or blocked decision

## Continuity File

Use exactly one primary continuity file in this order:

1. user-specified status file
2. existing repo continuity file such as `session-handoff.md`, `handoff.md`, or `progress.md`
3. workspace-root `STATUS.md`

If the task will span multiple slices and no file exists, create `STATUS.md`.

Keep it short:

- goal
- baseline
- done criteria
- done
- in progress
- next
- blockers
- verification

## Done and Blocked

Default done means:

- the requested work is complete
- safe in-scope fixes were made
- relevant verification ran
- the result was checked against the goal and baseline
- the primary continuity file was updated
- required acceptance items are all `done` or explicitly `blocked`

Real blockers are limited to:

- missing credentials, secrets, or permissions that cannot be discovered locally
- unavailable external dependencies required for the next proof step
- conflicting requirements that cannot be resolved from prompt or repo evidence
- destructive or high-risk actions requiring explicit confirmation
- required verification blocked by an unavailable hard dependency

If blocked, report:

- what is done
- what is blocked
- evidence
- what was tried
- exact next action once unblocked

## End-of-Turn Check

Before ending the turn, confirm:

- the requested outcome or current slice is actually finished
- the completion ledger has no unclosed required items
- the strongest practical verification has run
- docs, status, and plans do not still describe finished work as pending
- no obvious next slice was left undone without a real blocker
- if blocked, the blocked proof step and the next action are both written down

## Observation Loop

Review real long-run sessions instead of relying on memory.

Use:

- `long-run-review-template.md` for postmortems
- `pressure-corpus.md` for reusable regression scenarios

Tune the skill from repeated failure shapes, not one-off vibes.

## Minimal Prompt

```text
Use long-run-execution.

Goal:
<goal>

Baseline:
<files or directories, if any>

Constraints:
<only task-specific constraints>
```
