# codex-skills

Practical Codex skills for execution-heavy agent workflows.

> Built for real work: repo cleanup, continuous execution, verification-first progress, and low-noise agent behavior.

[中文说明](./README_CN.md) · [Contributing](./CONTRIBUTING.md)

## What this repository is

`codex-skills` is a small, focused collection of reusable Codex skills designed for agent workflows that need to actually move work forward.

These skills are not generic prompt snippets. They are structured, reusable operating guides for common execution problems such as:
- slimming AI-generated repositories without damaging active contracts
- keeping long tasks moving through verified slices instead of drifting into handoff theater
- reducing repo pollution from tools and intermediate artifacts
- making skill behavior stable enough to reuse across repositories

## Who this is for

This repository is for people who use Codex as an execution agent and want:
- stronger repository hygiene
- more reliable long-running execution behavior
- reusable skills instead of rewriting prompts every time
- execution outputs that are concrete, verified, and low-noise

## Included skills

### `ai-repo-cleanup`
A deletion-oriented repository slimming skill for AI / agent codebases.

Use it when a repository keeps accumulating:
- dead code suspicion
- false-alive tests
- weak helper/support splits
- duplicate or low-value support surfaces
- stale docs/history noise that should not dominate the active repo

What makes it different:
- focuses on **safe deletion value**, not generic code review
- produces an **execution package**, not a vague audit report
- supports **zero-action compression** when no cleanup should happen
- requires tool artifacts to stay outside the repo by default
- explicitly forbids GitNexus-style instruction-file pollution such as `AGENTS.md` / `CLAUDE.md`

### `long-run-execution`
A skill for keeping Codex moving through long tasks without drifting into midpoint summaries or fake handoffs.

Use it when the user wants:
- uninterrupted execution
- verification after each slice
- continued progress until the next real milestone
- fewer “next agent can continue” style outputs

What makes it different:
- locks the current slice around target, boundary, and proof
- pushes verification into the pacing loop
- treats handoff-as-substitute-for-work as failure
- keeps continuity short and execution-oriented

## Typical use cases

### Example: repository cleanup
User says:

```text
Use ai-repo-cleanup to audit this repo and generate a cleanup list.
```

Expected outcome:
- delete-ready and high-probability cleanup items are front-loaded
- tool outputs stay out of the repo
- the coding agent can act on the result directly

### Example: long execution session
User says:

```text
Keep going until this feature is implemented and verified.
```

Expected outcome:
- Codex does not stop at a midpoint summary
- each slice is verified before moving on
- continuity reflects actual progress instead of speculative notes

## Design principles

This repository prefers skills that are:
- **execution-first**
- **verification-driven**
- **small in scope, strong in rules**
- **useful across repositories**
- **careful about repo hygiene**

Non-goals:
- building a giant skill framework
- packaging every personal prompt into a public repo
- adding heavy setup just to make simple skills look “productized”

## Installation

### Install all bundled skills

```bash
cd codex-skills
./scripts/install.sh
```

### Install one skill only

```bash
cd codex-skills
./scripts/install.sh ai-repo-cleanup
```

### Install to a custom Codex home

```bash
CODEX_HOME=/path/to/custom/codex ./scripts/install.sh
```

Default target:

```bash
$HOME/.codex/skills
```

## Repository layout

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
- better skill examples and before/after outputs
- optional release notes for skill behavior changes

The repo will stay intentionally small.

## License

MIT
