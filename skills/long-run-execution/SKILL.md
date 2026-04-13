---
name: long-run-execution
description: Use when a task spans multiple milestones, the user wants uninterrupted execution to the next verified outcome, or the user says to keep going without midpoint handoff, re-planning, or “next agent” transfer output
---

# Long-Run Execution

## Overview

Use this when the user wants sustained execution, not a midpoint summary.

Default stance: keep moving until one of these is true:

- the requested outcome is complete and verified
- the current executable slice is complete and the next slice is blocked by a real blocker
- a destructive or high-risk action needs explicit confirmation

Anything else is not a stopping condition.

## Hard Rules

- Do not stop at analysis if the next slice is executable now.
- Do not replace execution with a handoff, transfer note, or “next agent can continue”.
- Do not turn the next obvious step into a suggestion for the user.
- Do not let documentation work become a substitute for implementation when implementation is already in scope.
- Do not let review/audit/plan-check tasks stop at findings if safe repair is in scope.
- Do not widen scope because of interesting side issues; log them and return to the active slice.
- Do not claim done without verification evidence.
- If a check fails, return to fixing. Do not switch to summary mode while the active slice is still broken.

## Goal Lock

At the start of each slice, write down three things internally and keep them stable until the slice is done:

1. `Target outcome` — what user-visible result is being advanced right now
2. `Boundary` — which files, modules, docs, or behaviors are in scope for this slice
3. `Proof` — which command, test, smoke check, or consistency check will prove the slice

If current work no longer serves one of those three items, stop and realign before editing more.

## Execution Loop

For each slice:

1. Read the current source of truth first:
- prompt
- relevant repo docs / plan / spec
- primary continuity file

2. Lock the smallest useful executable frontier:
- not the whole milestone
- not a vague phase
- one slice that can be changed and verified now

3. Execute only work that directly advances that frontier:
- prefer direct edits over more planning
- prefer finishing one slice over opening multiple partial branches
- if you find non-blocking problems, record them and keep going

4. Run slice verification immediately:
- code: targeted test / build / lint / smoke
- docs: cross-reference / entry-path / consistency check
- config: parse / load / startup validation
- scripts or data: sample run or output validation

5. Re-check alignment:
- compare changes against prompt, baseline docs, and active done criteria
- check for over-engineering, fake fallbacks, or test-only behavior
- confirm the change solved the intended slice, not a nearby problem

6. Sync reality:
- update the primary continuity file
- sync affected plan / checklist / README / handoff docs that now drift from reality

Then continue to the next executable slice.

## Verification Cadence

Verification is not a final-step ceremony. It is the pacing mechanism for long tasks.

- Before editing, decide what proof will be run for the slice.
- After each slice, run the narrowest relevant check.
- After each milestone, run the broader regression that matches the risk.
- Before ending the turn, run the strongest practical final check for the claimed state.

If “full end-to-end” is required but not yet affordable, keep progressing through verified sub-slices until the only missing proof is the end-to-end check itself.

## Anti-Drift Rules

- If the user gave a plan/spec/design, treat it as the active boundary unless runtime evidence disproves it.
- Keep a short invariant list for the task, such as “thin harness only”, “no new architecture”, “tests must pass”, or “preserve existing API”.
- Re-check those invariants after every slice.
- If another skill would introduce approval waits, brainstorming, or document-first detours, do that only when the user explicitly asked for design/planning or when execution is truly blocked without it.
- “I prepared a document for the next agent” is failure unless the user explicitly asked for that deliverable.

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

## Default Done Criteria

If the user did not define done precisely, infer it from the task. Default done means:

- the requested work is complete
- safe in-scope fixes were made
- relevant verification ran
- the result was checked against the goal and baseline
- the primary continuity file was updated

For review / audit / plan-vs-implementation tasks, also require:

- baseline docs or plans were read first
- omissions, breakages, unreasonable implementation, and drift were identified
- safe repairs were completed when in scope
- alignment was re-checked after repair
- affected plan / status / entry docs were synchronized

## Real Blockers

Only stop for:

- missing credentials, secrets, or permissions that cannot be discovered locally
- unavailable external dependencies required for the next proof step
- conflicting requirements that cannot be resolved from prompt or repo evidence
- destructive or high-risk actions requiring explicit confirmation
- required verification blocked by an unavailable hard dependency

Time spent, task size, fatigue, or the ability to write a polished summary are not blockers.

If blocked, report:

- what is done
- what is blocked
- evidence
- what was tried
- exact next action once unblocked

## Audit Mode

When checking whether code matches a plan, design, spec, or execution checklist:

1. Read the baseline docs first.
2. Treat them as source of truth unless runtime evidence or the user overrides them.
3. Inspect for missing implementation, broken paths, unreasonable choices, and drift.
4. Produce a concrete issue list.
5. If repair is safe and in scope, continue directly into repair.
6. Run targeted verification.
7. Re-check alignment after repair.
8. Sync affected status / plan / entry docs.

Do not stop at the issue list if repair is actionable.

## Completion Check

Before ending the turn, confirm:

- the requested outcome or current slice is actually finished
- the strongest practical verification has run
- docs/status/plan entries do not still describe finished work as pending
- no remaining obvious next slice was left undone without a real blocker

## Completion Sync Check

Before ending the turn on a long-running task, check whether repo documents that guide future work still match reality:

- continuity or status files
- handoff or transfer docs
- execution plans or checklist plans
- README or docs indexes used as entry points

At minimum, confirm:

- completed work is not still marked pending
- next steps do not repeat finished work
- recommended entry paths still match the current implementation
- drift conclusions are written down when relevant

## Final Report

When ending the turn, include:

- completed work
- issues found
- changes made
- current status
- next step, if any
- verification results

Include blocker details if blocked.

## Observation Loop

To improve this skill over time, review real long-run sessions instead of relying on memory.

Track these signals:

- Did the agent stop while an executable slice still existed?
- Did it replace execution with handoff, planning, or a transfer note?
- Did it run proof after each slice or only at the end?
- Did it drift outside the active boundary?
- Did it over-engineer, add fake fallbacks, or write test-only behavior?
- Did it keep status / plan / README guidance synchronized with reality?
- Did it stop only for a real blocker?

When a session is worth learning from, record it with the template in `long-run-review-template.md`.

Prefer examples with concrete evidence:

- the user request
- the stopping point
- the missing next slice
- the proof that should have run
- the exact rule the skill needs to add or tighten

Do not generalize from a vibe. Generalize from repeated failure shapes.

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
