---
name: ai-repo-cleanup
description: Use when an AI or agent repository shows dead code suspicion, duplicate intent, compatibility residue, wrapper sprawl, helper drift, or test and docs growth and needs a deletion-oriented cleanup audit before edits.
---

# AI Repo Cleanup

## Overview

Audit a repository for **cleanup candidates worth proving or removing** before edits.

This skill is aggressive in candidate discovery and conservative in final deletion verdicts. It should surface what may be removed, merged back, narrowed, retired, or archived, then name the missing proof clearly enough for a coding agent to continue.

Default package:
- one repo-level execution package
- module execution sheets only for candidates with immediate execution value

The package must answer:
**what should be cleaned now, what should be challenged next, what proof is missing, and what verification keeps the main chain safe?**

## When to Use

Use when:
- an AI / agent repo keeps growing after repeated assisted edits
- there is suspicion of dead code, duplicate logic, compatibility residue, wrapper sprawl, weakly justified helpers, or false-alive paths
- the user wants a deletion-oriented audit that produces execution candidates, not just code quality commentary
- one analysis round should drive one real cleanup round

Do not use when:
- the task is only style cleanup, naming cleanup, or comment cleanup
- the user already has an approved cleanup plan and wants code edits immediately
- the repo is not meaningfully AI / agent / harness related

## Core Rules

1. **Maximize candidate discovery before verdict compression.**
2. **Do not hide plausible cleanup candidates just because proof is incomplete.**
3. **Audit first; no code edits by this skill unless the user explicitly asks.**
4. **Runtime and producer evidence outrank graph and code-shape heuristics.**
5. **Static signals and size signals are candidate generators, not deletion verdicts.**
6. **Prefer explicit candidate lists over over-compressed hold summaries.**
7. **Do not recommend deletion without stating what surviving contract remains and how to verify it.**
8. **Tooling must not pollute the user repository by default.**
9. **Missing tools do not cancel the audit.**
10. **Repository surface size guides audit ordering; it does not justify deletion by itself.**
11. **Do not default to sending the user a large command checklist before producing the first audit package.**
12. **Start with the strongest available in-context evidence, then name only the minimal missing proof.**
13. **When code/test cleanup and doc cleanup are both actionable, front-load code/test cleanup unless docs are the only delete-ready slice or are blocking execution.**
14. **Large grouped candidates must declare current-round maturity and immediate execution value.**
15. **Every cleanup execution package must carry a verification matrix, churn expectation, and expected residuals.**
16. **If in-repo output is requested, keep exactly one live checklist document per cleanup wave.**
17. **Persisted repo docs must use repo-relative paths only.**
18. **High-Probability Next should stay intentionally short and represent one focused execution wave.**
19. **Large grouped candidates must include candidate files, first-batch exact targets, and candidate-level verification.**
20. **Each wave should compare itself with the previous wave for the same repo and report stability or drift.**

## Candidate Policy

The skill should surface candidates from any repository role, including runtime code, support layers, tests, docs, tooling, and historical residue.

Good candidate signals include:
- no clear producer
- weak reachability
- duplicate implementation or duplicate intent
- thin wrappers or compatibility shims
- single-consumer support splits
- non-core surface that grew faster than the active spine
- helper, adapter, builder, fixture, or utility layers with weak ownership
- paths kept alive only by narrow or historical callers

Actionability matters too:
- duplicate helper pairs with a plausible canonical owner should outrank broader mapping work
- strong merge-back candidates with caller / constructor / registration proof should outrank diffuse backlog items
- large test families should be compressed into the shortest execution wave a coding agent can actually run

A candidate may be listed even when proof is incomplete, but the missing proof must be named.

## Missing Proof Types

Use one or more of these labels for every non-ready candidate:
- `runtime-proof` — whether a live startup, request, job, or loop still touches it
- `producer-proof` — whether current code still emits, registers, or constructs it
- `caller-proof` — whether real imports, call sites, or registrations still exist
- `contract-proof` — what surviving API, config, or test contract would break if it vanished
- `owner-proof` — whether the path still has a justified owner role instead of historical drift

If proof is missing, say the **fastest next check** instead of stalling the audit.

## Candidate Entry Schema

For each item in `delete-ready now`, `high-probability next`, or `aggressive candidate backlog`, include:
- `path-or-group`
- `candidate-type`
- `key-evidence`
- `surviving-contract`
- `missing-proof`
- `fastest-next-check`
- `suggested-action`

Keep entries compact, but do not omit `surviving-contract` or `missing-proof`.

## Grouped Candidate Maturity

If a candidate spans `3+` files, multiple owners, or roughly `1000+` lines, include these extra fields:
- `cluster-size`
- `current-round-maturity`
  - `ready-first-batch`
  - `proof-first`
  - `mapping-first`
  - `hold`
- `first-batch-exact-targets`
- `expected-immediate-deletions`
- `proof-blockers`
- `candidate-files`
- `candidate-verification`

This is required for large test families, transport/finalization seams, delivery/channel bundles, session/context clusters, or similar grouped cleanup targets.

## Large Test Family Rule

For any test cluster that is broad enough to risk owner drift, the audit must output a three-stage package:

1. `owner map`
   - which suite owns which behavior
2. `deletion list`
   - exact first-batch assertions, files, or blocks to remove or move
3. `execution checklist`
   - the order to delete, verify, and stop

Do not send a large test family straight from broad suspicion into execution. The coding agent should already know the owner boundary before deleting.

Default threshold:
- `3+` files with overlapping assertions, or
- `1200+` total lines, or
- one family still mixes acceptance, contract, rendering, transport, and loop ownership in the same wave

## Output Classes

Compress findings into five useful classes:
- `delete-ready now`
- `high-probability next`
- `aggressive candidate backlog`
- `expected residuals`
- `not-a-cleanup-priority`

Rules:
- `aggressive candidate backlog` is required when plausible cleanup targets exist but proof is not yet sufficient
- `expected residuals` is required whenever the current round will intentionally leave known hits behind
- do not bury meaningful candidates inside generic `later-phase` prose
- if the round found one strong target and several weaker ones, list them all with different evidence grades
- keep `high-probability next` intentionally short; default target is `5-8` items
- prefer the most executable items first, even when broader families have larger raw scores

## Required Final Output Shape

Always finish with a cleanup execution package.

Use this shape unless the user requested another exact format:

### Delete-Ready Now
- items with the full candidate entry schema

### High-Probability Next
- items with the full candidate entry schema

### Aggressive Candidate Backlog
- items with the full candidate entry schema

### Expected Residuals
- `path-or-group`
- `why it remains`
- `what proof or design unlocks it later`

### Not-a-Cleanup-Priority
- `path-or-group`
- `why it stays out of scope this round`

### Cleanup Execution Package
- `scope`
- `ordered-actions`
- `verification-matrix`
- `churn-expectation`
- `expected-residuals`
- `stop-conditions`
- `current-wave action board`
- `wave stability`

The first useful output should already use this structure. Do not postpone it behind a broad command dump.

`current-wave action board` should make the next coding wave obvious:
- exact candidate files when known
- first-batch exact targets
- preferred canonical owner for duplicate helpers when known
- candidate-level verification proofs

`wave stability` should compare the current wave with the previous wave for the same repo:
- new candidates
- promoted candidates
- resolved candidates
- persistent candidates

## Verification Matrix

Every cleanup execution package must carry a verification matrix. Use repo-native names when they already exist.

Always specify the smallest relevant set from:
- `owner tests`
- `protected regression`
- `execution-path regression`
- `end-to-end smoke`
- `docs and hygiene checks`

For each entry, include:
- `purpose`
- `fastest command or proof`
- `pass signal`

If the repository has a real request chain, agent loop, or delivery path, `end-to-end smoke` should be present unless the audit explicitly proves that the current round cannot affect it.

For the current-wave action board, also include per-candidate verification whenever possible:
- `owner tests`
- `protected regression`
- `execution-path regression` for active runtime seams

## Churn Expectation

Every cleanup execution package must estimate the likely shape of the wave:
- `expected-code-delta`
- `expected-test-delta`
- `expected-docs-delta`
- `expected-net-line-direction`

Approximate ranges are enough. The point is to prevent false expectations about a wave that deletes code but temporarily grows docs or checklists.

## Single-Live-Checklist Rule

When the user wants in-repo output:
- keep one live cleanup checklist document for the wave
- keep owner maps, deletion lists, and execution checklists as sections or appendices of that live doc unless the user explicitly wants separate files
- never leave multiple active backlog pointers alive at once
- once a wave is closed, compress its execution history into one short archive summary or durable changelog note

## Execution Framing

When the user wants documents a coding agent can act on, make these points explicit:
- the audit is complete for the current round
- the document is an execution handoff, not a request to reopen broad analysis
- `needs-proof` means gather the named proof and keep moving
- do not frame the goal as analysis-only unless the user explicitly asked for analysis-only output
- do not require optional tools or fresh indexes unless they are the fastest missing proof

## Zero-Action Round Rule

If all three are true:
- `Delete-ready Now` is empty
- `High-Probability Next` is empty
- there is no meaningful `Aggressive Candidate Backlog`

then switch to zero-action mode immediately:
- output one short repo-level execution package
- do not generate module execution sheets by default
- state clearly that the current round found no new cleanup action
- stop expanding analysis unless the user asks for a broader challenge round

## Common False Positives

Do not treat these as deletion wins without stronger proof:
- test helpers that encode contract boundaries
- adapters that are the only protocol or provider boundary
- docs paths still referenced by active workflows or indexes
- runtime registration indirection mistaken for no-caller code
- support files carrying real retry, normalization, or error policy behavior

## Artifact Hygiene

- Never let audit tooling write repo-local artifacts by default.
- Prefer `/tmp/skill/ai-repo-cleanup/runs/<timestamp>/...` for generated outputs.
- Treat generated instruction files as pollution unless explicitly requested. This includes `AGENTS.md`, `CLAUDE.md`, `TOOLS.md`, `SOUL.md`, and `BOOTSTRAP.md`.
- If any tool creates instruction-file pollution, delete or externalize it before finishing.
- Final audit documents default to `/tmp`; only persist inside `docs/` when the user requests in-repo output.
- Persisted repo docs must not use machine-local absolute paths.

## Environment and Portability

- Default assumption: only system `python3` and basic shell tools are available.
- Audit scripts must run without creating or activating a virtual environment.
- Do not require project dependency installation for the default audit path.
- Do not import the target repository's runtime code from audit scripts.
- Language-aware symbol tools are optional strengthening evidence, never mandatory.
- If a stronger tool is missing, continue with the strongest remaining evidence and mark unresolved items `needs-proof`.

## Evidence Priority

Prefer evidence in this order:
1. active execution path and current runtime behavior
2. direct imports, call sites, registrations, config wiring
3. tests and fixtures showing what is still exercised
4. docs or ADRs explaining why a path exists
5. git evidence showing growth and drift
6. graph or index tools
7. code-shape and size heuristics

## Repository Surface Snapshot

In `repo-scan` mode, capture one lightweight repository surface snapshot early.

Use it to:
- estimate where tracked repo surface lives
- decide which roles deserve earlier attention
- spot growth outside the active spine

Rules:
- classify by **role**, not fixed directory names
- treat the snapshot as an audit-ordering signal, not a deletion verdict
- keep generated or vendor surface out of the primary slimming baseline unless explicitly requested
- if classification is unclear, keep the file in `unknown-or-mixed`
- read `references/repo-surface-snapshot.md` when structure or classification is non-obvious

## Tool Adapters

Use tools as optional evidence sources:
- shell / `rg` / `git` / small scripts as the default baseline
- graph and static tools as optional evidence multipliers
- coverage or targeted tests as optional proof
- language-aware symbol tools as optional strengthening evidence

Tools may help discover:
- weak reachability
- duplicate symbols or duplicate intent
- thin wrappers
- single-consumer splits
- role concentration
- symbol reference gaps

Read `references/output-schema.md` for stable report shapes.
Read `references/candidate-census-design.md` when extending census scripts.
Read `references/cleanup-checklist.template.md` when persisting one in-repo wave checklist.
Read `references/module-cleanup-checklist.template.md` when generating module execution sheets.

## Modes

### Branch Scan
Use for current-branch cleanup planning.
- compare the branch to merge base
- inspect changed modules first
- decide whether growth is convergence, duplication, fallback growth, or false slimming
- output current-branch actions before repo-wide backlog

### Repo Scan
Use for whole-repository slimming governance.
- capture one role-based repository surface snapshot before deep discovery
- determine goal and active spine
- inspect hotspots with git, source, tests, docs, and optional graph tools
- identify delete-ready slices, residue, weakly justified support splits, duplicate logic, and high-suspicion dead paths
- output repo-wide priorities plus module execution sheets only for current-round actions

## Audit Flow

### Phase 1 — Repository Understanding
Establish:
- repository goal
- runtime model
- active spine
- core vs supporting vs edge modules
- role-based surface distribution
- growth hotspots
- where recent AI-assisted growth concentrated

Output:
- one compact statement of goal and active spine
- one compact statement of audit ordering

### Phase 2 — Discovery Pass
Audit for:
- dead code suspicion
- weakly reachable code
- duplicate implementations and duplicate intent
- thin wrappers and compatibility residue
- support or helper splits with weak ownership
- visibility-gap paths missing from runtime, docs, and graph signals
- cleanup concentration signals where one role has grown faster than the active spine

Output:
- candidate lists grouped by evidence strength, not a long narrative

### Phase 3 — Reachability and Producer Pass
Explicitly answer:
- who still produces the suspicious branch or payload?
- who still calls, imports, or registers the suspicious path?
- is the path runtime-alive, test-alive, docs-only, or historical?
- does the split have more than one real consumer?
- what narrower owner contract survives if a broad path is retired?

Output:
- one missing-proof line per non-ready candidate
- one surviving-contract line per delete-oriented candidate

### Phase 4 — Verdict Compression
Compress findings into:
- `delete-ready now`
- `high-probability next`
- `aggressive candidate backlog`
- `expected residuals`
- `not-a-cleanup-priority`

Do not let hold material dominate the output.

### Phase 5 — Execution Packaging
Produce one cleanup execution package that already answers:
- what to do first
- which grouped candidates are mature enough for current execution
- what exact first-batch deletions are realistic this round
- what verification protects the main chain
- what residual hits are intentionally left behind

## Output Requirement

Always finish with a cleanup execution package.

The output must:
- front-load `delete-ready now` and `high-probability next`
- keep an explicit `aggressive candidate backlog`
- keep an explicit `expected residuals`
- state the missing proof for each non-ready candidate
- state grouped-candidate maturity for large clusters
- include a verification matrix and churn expectation
- help a coding agent continue cleanup without reopening broad analysis
