# codex-skills

<div align="center">

Execution-first Codex skills for repository cleanup, long-running agent work, and low-noise verified progress.

[中文文档](./README_CN.md) · [Contributing](./CONTRIBUTING.md) · [ai-repo-cleanup](./skills/ai-repo-cleanup/README.md) · [long-run-execution](./skills/long-run-execution/README.md)

![Skills](https://img.shields.io/badge/skills-2-black?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Focus](https://img.shields.io/badge/focus-execution--first-blue?style=flat-square)

</div>

`codex-skills` is a small open-source repository of practical Codex skills built for one narrow goal: make execution-oriented agent work more reliable, more reusable, and less noisy.

The current center of gravity is:

`repo cleanup -> verified execution -> low-noise continuity`

If a skill does not help Codex produce clearer execution, safer cleanup, or stronger verification, it probably does not belong here.

## Overview

- execution-first Codex skills
- verification before claims
- repository hygiene by default
- low-noise outputs over analysis theater
- one repository, multiple focused skills

## Why This Exists

Many prompt collections look impressive but are hard to reuse, hard to maintain, and too soft when real work begins. `codex-skills` is intentionally narrower.

It focuses on skills that improve real execution behavior, such as:
- slimming AI-generated repositories without damaging active contracts
- keeping long tasks moving through verified slices instead of drifting into handoff theater
- preventing tools and intermediate outputs from polluting user repositories
- turning repeatable execution patterns into reusable Codex skills instead of rewriting prompts every time

## At A Glance

| Skill | Responsibility |
| --- | --- |
| `ai-repo-cleanup` | surface delete-ready, high-probability, and backlog cleanup candidates in AI / agent repositories with explicit missing proof |
| `long-run-execution` | keep Codex executing through verified slices until the next real milestone instead of drifting into summaries, handoffs, or fake blockers |

## Included Skills

### `ai-repo-cleanup`
A deletion-oriented cleanup audit for AI / agent codebases that challenges what should be removed, merged back, narrowed, retired, or archived before edits.

Best for:
- dead code suspicion
- false-alive tests
- weak helper/support splits
- duplicate implementation or duplicate intent
- wrappers, adapters, compat layers, and other support seams
- stale docs/history noise and non-core surface growth that should not dominate the active repo

Key characteristics:
- maximizes candidate discovery before verdict compression
- produces an **execution package**, not a vague audit report
- names the **missing proof** and fastest next check for non-ready candidates
- supports **zero-action compression** when no cleanup should happen
- requires tool artifacts to stay outside the repo by default
- explicitly forbids GitNexus-style instruction-file pollution such as `AGENTS.md` / `CLAUDE.md`

### `long-run-execution`
A skill for keeping Codex moving through long tasks without collapsing into midpoint summaries, fake handoffs, blocker inflation, or user-question loops for locally discoverable context.

Best for:
- uninterrupted execution
- verification after each slice
- progress to the next real milestone
- reducing “next agent can continue” style drift
- audit-then-repair tasks that should not stop at issue lists

Key characteristics:
- locks the current slice around target, boundary, and proof
- adds an explicit continue / stop decision ladder
- makes verification part of execution cadence
- classifies side issues and returns to the active slice
- treats handoff-as-substitute-for-work as failure
- keeps continuity short and reality-based

## Typical Use Cases

### Repository cleanup

```text
Use ai-repo-cleanup to audit this repo and generate a cleanup list.
```

Expected outcome:
- delete-ready and high-probability items are front-loaded
- tool outputs stay out of the repo
- a coding agent can act on the result directly

### Long execution session

```text
Keep going until this feature is implemented and verified.
```

Expected outcome:
- Codex does not stop at a midpoint summary
- each slice is verified before moving on
- continuity reflects actual progress instead of speculative notes

## Design Principles

`codex-skills` prefers skills that are:
- **execution-first**
- **verification-driven**
- **small in scope, strong in rules**
- **useful across repositories**
- **careful about repository hygiene**

Non-goals:
- building a giant skill framework
- packaging every personal prompt into a public repo
- adding heavy setup just to make simple skills look productized

## Repository Layout

```text
codex-skills/
  README.md
  README_CN.md
  CONTRIBUTING.md
  LICENSE
  scripts/
    install.sh
  skills/
    ai-repo-cleanup/
      README.md
      SKILL.md
      references/
      scripts/
    long-run-execution/
      README.md
      SKILL.md
      long-run-review-template.md
```

## Quick Install

Install all bundled skills:

```bash
cd codex-skills
./scripts/install.sh
```

Install only one skill:

```bash
cd codex-skills
./scripts/install.sh ai-repo-cleanup
```

Install to a custom Codex home:

```bash
CODEX_HOME=/path/to/custom/codex ./scripts/install.sh
```

Default target:

```bash
$HOME/.codex/skills
```

## Development

Edit skills in place under:

```bash
skills/<skill-name>/
```

Reinstall locally after changes:

```bash
./scripts/install.sh
```

Test without touching your real Codex home:

```bash
CODEX_HOME=$PWD/.tmp/codex-home ./scripts/install.sh ai-repo-cleanup
```

## Roadmap

Possible future additions:
- more execution-oriented skills from the same workflow family
- richer examples and before/after outputs
- lightweight release notes for behavior changes

The repository will stay intentionally small.

## 🏠 Commuity （Acknowledge）

First shared on [LINUX DO](https://linux.do/) — where possible begins.

## License

MIT
