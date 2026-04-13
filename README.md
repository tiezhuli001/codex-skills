# codex-skills

Open-source Codex skills for agentic execution workflows.

Currently included:
- `ai-repo-cleanup` — deletion-oriented repository slimming audit
- `long-run-execution` — keep executing through verified slices without midpoint handoff drift

## Why this repo

This repository packages a small set of practical Codex skills that work well together:
- repo cleanup and slimming
- long-running execution discipline
- reusable installation and release layout

It is organized as **one repository, multiple skills** so each skill can stay independent while sharing:
- installation flow
- documentation style
- versioning
- examples

## Repository layout

```text
codex-skills/
  README.md
  README_CN.md
  LICENSE
  scripts/
    install.sh
  skills/
    ai-repo-cleanup/
      SKILL.md
      references/
      scripts/
    long-run-execution/
      SKILL.md
```

## Quick install

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

By default this installs into:

```bash
$HOME/.codex/skills
```

You can override the destination with `CODEX_HOME`:

```bash
CODEX_HOME=/path/to/custom/codex ./scripts/install.sh
```

## Included skills

### `ai-repo-cleanup`
Use when an AI/agent repository needs a deletion-oriented slimming audit that finds:
- dead code suspicion
- false-alive tests
- weak helper splits
- redundant support surfaces
- archive/doc noise that should not dominate the active repo

### `long-run-execution`
Use when the user wants uninterrupted execution through verified slices and does **not** want midpoint handoff behavior.

## Development

To update a skill in this repo, edit the files under `skills/<skill-name>/`.

To reinstall locally after changes:

```bash
./scripts/install.sh
```

## License

MIT
