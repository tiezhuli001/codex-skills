# Long-Run Execution Review Template

Use this after a real session that invoked `long-run-execution`.

## Metadata

- Date:
- Session path:
- Repo / workspace:
- Task type: implementation / audit / plan-check / docs / mixed
- Outcome: success / partial / drift / blocked / false-finish

## User Intent

- Goal:
- Baseline:
- Constraints:
- Explicit completion bar:

## What Actually Happened

- Last meaningful executed slice:
- Where the agent stopped:
- What it reported as the reason for stopping:
- Was another executable slice still available? yes / no
- If yes, what was the missed next slice?

## Verification Behavior

- Slice-level proof run:
- Milestone-level proof run:
- Final proof run:
- Missing proof:
- Did the agent claim success without proof? yes / no

## Drift Check

- Did execution stay inside the active boundary? yes / no
- If no, what drift happened?
- Did the agent add unnecessary architecture / fallback / scaffolding? yes / no
- Did docs/status/plan stay synced? yes / no

## Blocker Check

- Was the stop caused by a real blocker? yes / no
- Evidence:
- What was tried before stopping:
- Exact next action once unblocked:

## Failure Shape

- Category:
  - stopped-too-early
  - handoff-instead-of-execution
  - missing-slice-proof
  - drifted-from-goal
  - over-engineered
  - fake-blocker
  - docs-out-of-sync
  - false-finish
- Short summary:
- Concrete evidence lines / files / commands:

## Skill Update Candidate

- Existing rule that should have caught this:
- Why it was insufficient:
- New or tightened rule proposal:
- Is this a one-off or repeated pattern?
- Similar sessions:

## Decision

- No skill change needed
- Tighten wording
- Add anti-pattern
- Add stronger stop rule
- Add verification rule
- Add audit / sync rule
