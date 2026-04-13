---
name: ai-repo-cleanup
description: Use when an AI or agent repository keeps growing through dead code suspicion, duplicate test surfaces, compatibility residue, weakly reachable helpers, or false-alive paths and needs a deletion-oriented slimming audit before edits
---

# AI Repo Cleanup

## Overview

Audit a repository for **safe deletion value** before edits.

This skill exists to find what can be removed, retired, narrowed, merged back, or archived with high confidence. Runtime evidence, graph tools, static heuristics, and code-shape signals are inputs. The goal is a **cleanup execution package** that helps a coding agent actually slim the repo.

Default package:
- one repo-level execution package
- module execution sheets only for items that are actionable in the current round

The package must answer one question clearly:
**what should be deleted or retired in this round, and what proof is still needed for the rest?**

## When to Use

Use when:
- an AI / agent repo keeps growing after repeated assisted edits
- there is suspicion of dead code, duplicate paths, false-alive tests, helper sprawl, or historical residue
- the user wants a deletion-oriented audit that leads directly to cleanup work
- the repository needs one analysis round that can drive one real cleanup round

Do not use when:
- the task is only style cleanup, naming cleanup, or comment cleanup
- the user already has an approved cleanup execution plan and wants code edits immediately
- the repo is not meaningfully AI / agent / harness related

## Core Rules

1. **Optimize for safe deletion value, not code quality scores.**
2. **Audit first; no code edits by this skill unless the user explicitly asks.**
3. **The output must help a coding agent remove code or tests, not just admire the repo.**
4. **Runtime and producer evidence outrank graph and code-shape heuristics.**
5. **Static quality signals are confidence multipliers, not deletion verdicts.**
6. **Front-load current-round deletions and retirements.**
7. **Do not recommend deletion without stating what active contract survives and how to verify it.**
8. **A repo-scan is not complete until each currently actionable module has a module execution sheet.**
9. **Tooling must not pollute the user repository by default.**
10. **Missing tools do not cancel the audit.**
11. **Default deliverable path is `/tmp/skill/ai-repo-cleanup/...`; write into the repo only if the user explicitly asks.**

## Anti-Slop Rules

The skill is failing if the output mainly does any of these:
- summarizes what is already completed instead of what should be done now
- spends more space on hold items than on deletions or high-probability retirements
- labels everything `later-phase` to avoid making decisions
- asks the coding agent to reopen broad analysis instead of naming the missing proof
- treats optional tools as mandatory gates
- produces module docs for noise that has no current execution value
- emits a long report when the current round has no actionable cleanup

If the current round has only two real delete-ready items, say so plainly. If there are ten, surface all ten. Do not inflate or hide.

## Execution Framing Requirements

When the user wants documents that a coding agent can act on, the output must make these points explicit:
- the audit is complete for the current round
- the document is a handoff for execution, not a request to reopen analysis
- the coding agent should start from `Execution Ladder` Phase 1 and continue until blocked by failed proof, failed verification, or evidence conflict
- `needs-proof` means gather the named proof and keep moving, not “come back next time”
- never frame the goal as “不改代码” unless the user explicitly requested analysis-only output
- never use report framing such as `对照`, `Current slimming goal`, `Baseline compared`, or similar audit-only headings
- do not require optional tools or fresh graph indexes unless the checklist names them as the fastest missing proof

## Zero-Action Round Rule

If both of these are true:
- `Delete-ready Now` is empty
- `High-Probability Next` is empty

then the skill must switch to **zero-action mode**:
- output one short repo-level execution package
- do **not** generate module execution sheets by default
- include at most one later-phase proof note if there is exactly one meaningful candidate worth keeping alive
- compress all hold/keep/not-a-target items into one short `Do Not Misclassify This Round` section
- state clearly that the current round contains no new cleanup action
- keep the document short; do not expand inventories just to prove that nothing should happen

## Artifact Hygiene

- Never let audit tooling write repo-local artifacts by default.
- Prefer `/tmp/skill/ai-repo-cleanup/runs/<timestamp>/...` for all generated outputs.
- If a tool insists on repo-local output, use a wrapper script to move or externalize the artifacts before continuing.
- Treat generated instruction files as pollution unless the user explicitly asked for them. This includes `AGENTS.md`, `CLAUDE.md`, `TOOLS.md`, `SOUL.md`, and `BOOTSTRAP.md`.
- GitNexus or related tooling must not create, replace, append to, or regenerate repository instruction files.
- If any tool creates instruction-file pollution, delete or externalize it before finishing and record the cleanup in the audit notes only if it materially affected the run.
- If unavoidable repo-local artifacts were created, restore repo cleanliness before finishing unless the user explicitly asked to keep them.
- Final audit documents default to `/tmp`; only persist inside `docs/` when the user requests in-repo output.

## Environment and Portability

- Default assumption: only system `python3` and basic shell tools are available.
- Audit scripts must run without creating or activating a virtual environment.
- Do not require `pip install`, `npm install`, `uv sync`, `poetry install`, or similar setup steps for the default audit path.
- Do not import the target repository's runtime code from audit scripts.
- If a stronger tool needs a project environment, treat it as optional and let the agent decide whether it is worth using.
- If `python3` or a helper tool is missing, degrade gracefully and mark unresolved items `needs-proof`.

## Evidence Priority

Prefer evidence in this order:
1. active execution path and current runtime behavior
2. direct imports, call sites, registrations, config wiring
3. tests and fixtures showing what is still exercised
4. docs or ADRs explaining why a path exists
5. git evidence showing growth and drift
6. graph / index tools such as GitNexus
7. code-shape and quality heuristics

## Tool Adapters

Use tools as optional evidence sources:
- **git / rg / shell / small scripts:** default baseline
- **GitNexus:** relationship graph, weak reachability, graph-missing paths
- **CodeQL / Semgrep / similar analyzers:** optional static signals when already available
- **coverage / test commands:** optional proof for false-alive tests

Rules:
- GitNexus is helpful, not mandatory.
- Graph tools are evidence sources, not deletion judges.
- If a tool is missing, continue with the strongest remaining evidence and mark unresolved items `needs-proof`.
- Do not force the coding agent to rebuild optional tool artifacts if the audit package already contains sufficient proof.
- GitNexus must be used in analysis-only mode for this skill; it must not bootstrap or rewrite repository instruction files such as `AGENTS.md` or `CLAUDE.md`.

## Modes

### Branch Scan
Use for current-branch cleanup planning.
- compare the branch to merge base
- inspect changed modules first
- decide whether growth is convergence, duplication, fallback growth, or false slimming

### Repo Scan
Use for whole-repository slimming governance.
- determine goal and active spine
- map core / supporting / edge modules
- inspect hotspots with git, source, tests, and optional graph tools
- identify delete-ready slices, false-alive tests, residue, weakly justified support splits, and high-suspicion dead paths
- produce one repo-level execution package plus module execution sheets only for current-round actions

## Audit Flow

### Phase 1 — Repository Understanding
Establish:
- repository goal
- runtime model
- active spine
- core vs supporting vs edge modules
- growth hotspots
- where recent AI-assisted growth concentrated

### Phase 2 — Discovery Pass
Audit for:
- dead code suspicion
- weakly reachable code
- false-alive tests
- compatibility or alias residue
- duplicate implementations and duplicate intent
- repeated fallback paths and broad exception fences
- support/helper splits with weak ownership
- visibility-gap paths missing from runtime, docs, and graph signals
- oversized or stale test families

### Phase 3 — Reachability and Producer Pass
Explicitly answer:
- who still produces the suspicious branch or payload?
- who still calls, imports, or registers the suspicious path?
- is the path runtime-alive or only test-alive?
- is the test protecting active behavior or only a historical wrapper?
- does the helper/support split have more than one real consumer?
- what narrower owner test survives if a broad test is retired?

Escalate suspicion when:
- a path is missing from runtime, docs, and graph signals together
- only tests keep the path alive
- the path has no real producer
- a support/helper file has one weak consumer and no independent ownership

### Phase 4 — Verdict Compression
Compress findings into only four useful classes:
- `delete-ready now`
- `high-probability delete or retire after one named proof`
- `later-phase only`
- `not-a-cleanup-target`

Do not let `later-phase` and hold material dominate the output.

### Phase 5 — Output Completion
Always finish with a cleanup execution package.
If the round has no actions, switch to zero-action mode.
If the round has actions, keep module sheets only for those actions.

## Deletion Threshold

Do **not** recommend deletion from any single signal alone:
- missing from graph
- no obvious reference from grep
- not in the main path
- file is large or ugly
- helper/support file exists
- code quality warning exists

A path becomes `delete-ready` only when the audit can explain most of these:
- no runtime caller
- no registration or config wiring
- no real producer
- only tests keep it alive, or owner tests cover the real contract already
- deletion preserves the active contract set
- verification after deletion is known and practical

A path becomes `high-probability` when:
- one missing proof is clearly named
- that proof is cheap and bounded
- the likely next action is still deletion, retirement, merge-back, or test narrowing

## Special Prioritization Rules

### Current-round value first
Every repo-level execution package should front-load:
- `Delete-ready Now`
- `High-Probability Next`
- `Later-phase Only`

The first screenful should show the current round of real work.

### Hold compression rule
Hold, keep, not-a-target, or already-completed items may appear only in one short section or one compact appendix.
Do not let them dominate the main checklist.

### Module sheet trigger rule
Generate a module execution sheet only when at least one is true:
- the module contains a `delete-ready` slice
- the module contains a `high-probability` slice
- the coding agent needs one concrete hold boundary this round to avoid a likely misdelete

If none apply, do not generate the module sheet.

### Weak support split rule
Do not promote a single-consumer support/helper split into the next execution phase unless at least one is true:
- it created a dedicated test file or a new test-only surface
- it materially increased repo surface area
- the boundary does not appear to have independent ownership
- it looks like file-thinning rather than contract isolation

Otherwise record it briefly and move on.

### Docs/archive rule
Docs and archive slimming default to `later-phase` unless:
- source-code delete-ready slices are exhausted, or
- the docs are actively blocking current execution, or
- references are clearly stale and easy to retarget safely

## Default Script Workflow

When stable scripts are available, prefer this order:
1. `scripts/prepare_tmp_workspace.py`
2. `scripts/repo_scan_snapshot.sh`
3. `scripts/test_surface_census.py`
4. `scripts/support_split_census.py`
5. `scripts/symbol_reachability_census.py`
6. `scripts/fallback_exception_census.py`
7. `scripts/complexity_budget_census.py`
8. optional `scripts/run_gitnexus_snapshot.sh`
9. optional `scripts/externalize_repo_artifacts.py`

All scripts should emit stable JSON into the active `/tmp` run directory.

## Output Contract

Default output is a cleanup execution package, not a patch and not a raw tool log.

Use:
- `references/cleanup-checklist.template.md` for the repo-level output
- `references/module-cleanup-checklist.template.md` for module-level outputs
- `references/output-schema.md` for JSON expectations
- `references/tool-adapters.md` for tool-role guidance
- `references/artifact-hygiene.md` for temp/output rules
- `references/environment-portability.md` for environment rules

Repo-level output should always include:
- `Scan Summary`
- `Audit Context`
- `Execution Intent`
- `Repository Goal and Module Map`
- `Delete-ready Now`
- `High-Probability Next`
- `Later-phase Only`
- `Execution Brief`
- `Execution Ladder`

Use these only when they add current-round execution value:
- `Module Coverage Map`
- `Do Not Misclassify This Round`
- `Main Spine Understanding`
- `Findings By Module`
- `Slimming Inventory`
- `Test Surface Census`

## Module Sheet Requirement

Generate a module execution sheet for:
- every `delete-ready now` module
- every `high-probability next` module
- at most one hold-boundary module when the coding agent is otherwise likely to misdelete it this round

Do not generate module sheets for zero-action rounds unless that one hold-boundary exception is truly necessary.

Every actionable module sheet should include:
- `Module Summary`
- `Execution Intent`
- `Decision Summary`
- `Per-File Execution Order`
- `Delete-ready or Retire-ready Slices`
- `Verification Baseline`
- `Module Execution State`

## Final Self-Check

Before finishing, confirm all of these are true:
- the repo document reads like a cleanup execution package, not a general audit report
- the first screenful shows what should be deleted, retired, or proved next
- the top section does not tell the next agent to avoid code edits unless the user explicitly asked for analysis-only output
- old report framing such as `对照` or `Current slimming goal` is absent
- hold material is compressed
- module sheets exist only where they add current-round execution value
- if the round has no actions, the output is short and uses zero-action mode
- optional tool outputs are referenced as evidence, not mandatory prerequisites
- all tool artifacts and scratch outputs stayed outside the repo unless the user asked otherwise
- no tool generated or modified repository instruction files such as `AGENTS.md` or `CLAUDE.md`

## Quality Bar

A good result:
- shows what can be deleted now within the first screenful
- shows what is highly likely to be deleted after one proof
- stays short when there is no action to take
- separates runtime-alive from test-only alive
- treats support/helper splits as evidence questions, not automatic deletions
- keeps docs/archive work behind source-code delete-ready work by default
- leaves a coding agent with a real cleanup list, not a museum of observations
