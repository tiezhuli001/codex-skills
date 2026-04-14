---
name: ai-repo-cleanup
description: Use when an AI or agent repository needs a deletion-oriented cleanup audit before edits because of dead code suspicion, duplicate intent, weak reachability, wrappers, helpers, adapters, support seams, compat or legacy layers, branch cleanup candidates, or non-core surface growth
---

# AI Repo Cleanup

## Overview

Audit a repository for **cleanup candidates worth proving or removing** before edits.

This skill is aggressive in candidate discovery and conservative only in final deletion claims. It should surface what may be removed, merged back, narrowed, retired, or archived, then name the missing proof clearly enough for a coding agent to continue.

Default package:
- one repo-level execution package
- module execution sheets only for candidates with immediate execution value

The package must answer:
**what should be cleaned now, what should be challenged next, and what proof is missing?**

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

## Output Classes

Compress findings into four useful classes:
- `delete-ready now`
- `high-probability next`
- `aggressive candidate backlog`
- `not-a-cleanup-priority`

Rules:
- `aggressive candidate backlog` is required when plausible cleanup targets exist but proof is not yet sufficient
- do not bury meaningful candidates inside generic `later-phase` prose
- if the round found one strong target and several weaker ones, list them all with different evidence grades

## Required Final Output Shape

Always finish with a cleanup execution package.

Use this shape unless the user requested another exact format:

### Delete-Ready Now
- items with the full candidate entry schema

### High-Probability Next
- items with the full candidate entry schema

### Aggressive Candidate Backlog
- items with the full candidate entry schema

### Not-a-Cleanup-Priority
- path or group
- why it stays out of scope this round

### Cleanup Execution Package
- `scope`
- `ordered-actions`
- `verification`
- `stop-conditions`

The first useful output should already use this structure. Do not postpone it behind a broad command dump.

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
- `not-a-cleanup-priority`

Do not let hold material dominate the output.

## Output Requirement

Always finish with a cleanup execution package.

The output must:
- front-load `delete-ready now` and `high-probability next`
- keep an explicit `aggressive candidate backlog`
- state the missing proof for each non-ready candidate
- help a coding agent continue cleanup without reopening broad analysis
