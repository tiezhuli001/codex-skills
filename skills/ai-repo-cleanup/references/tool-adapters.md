# Tool Adapters

## Purpose
Tools help gather evidence for deletion-oriented slimming. They do not decide deletions on their own.

## Preferred baseline
Use these first:
- `git`
- `rg`
- `find`
- `wc`
- small Python stdlib scripts

## Optional tools
### GitNexus
Use for:
- graph-visible vs graph-missing paths
- weak reachability checks
- duplicate cluster hints
- suspicious modules with few real callers

Rules:
- treat it as optional
- externalize repo-local artifacts
- never let graph evidence outrank runtime or producer evidence
- never allow it to generate, replace, or append repository instruction files such as `AGENTS.md`, `CLAUDE.md`, `TOOLS.md`, `SOUL.md`, or `BOOTSTRAP.md`
- if such files appear, treat them as tool pollution and clean them before finishing

### CodeQL / Semgrep / similar
Use only if already available and if they can produce signals relevant to deletion value:
- unreachable code
- broad exception fences
- duplicate or fallback-heavy clusters
- commented-out or dead-shape code

These tools provide hints, not verdicts.
