# Contributing

Thanks for contributing to `codex-skills`.

## Scope

This repository contains practical Codex skills for execution-heavy agent workflows.

Current bundled skills:
- `ai-repo-cleanup`
- `long-run-execution`

## Contribution expectations

Please keep contributions:
- small and reviewable
- execution-oriented
- consistent with the existing skill style
- focused on real agent behavior, not abstract framework churn

## Skill design guidelines

When editing or adding a skill:
- keep the skill focused on one clear job
- prefer hard rules over vague advice
- keep prompts and templates concise
- make outputs useful for real execution, not just analysis theater
- avoid introducing tool dependencies unless they materially improve outcomes
- make sure temporary artifacts do not pollute user repositories by default

## Repository conventions

- each skill lives under `skills/<skill-name>/`
- each skill should have its own `README.md`
- keep shared install logic under `scripts/`
- keep top-level docs lightweight

## Local workflow

Install all bundled skills locally:

```bash
./scripts/install.sh
```

Install one skill only:

```bash
./scripts/install.sh ai-repo-cleanup
```

Use a temporary Codex home if you want to test without touching your real setup:

```bash
CODEX_HOME=$PWD/.tmp/codex-home ./scripts/install.sh ai-repo-cleanup
```

## Pull requests / commits

Good changes usually include:
- the skill file update
- any required reference/template changes
- README updates when behavior or scope changed

Before submitting, do a quick sanity check:
- repository structure is still clean
- install script still works
- no accidental local-only artifacts were added
- wording stays consistent with execution-oriented use

## Non-goals

Please avoid:
- turning the repo into a generic framework
- adding heavy packaging before it is needed
- adding workflow noise that makes the skills harder to use
