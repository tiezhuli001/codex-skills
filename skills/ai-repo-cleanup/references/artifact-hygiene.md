# Artifact Hygiene

## Default rule
Audit tooling must not pollute the user repository.

## Default locations
- Run root: `/tmp/skill/ai-repo-cleanup/runs/<timestamp>/`
- Reports: `/tmp/skill/ai-repo-cleanup/runs/<timestamp>/reports/`
- Logs: `/tmp/skill/ai-repo-cleanup/runs/<timestamp>/logs/`
- Snapshots: `/tmp/skill/ai-repo-cleanup/runs/<timestamp>/snapshots/`
- Externalized tool artifacts: `/tmp/skill/ai-repo-cleanup/runs/<timestamp>/artifacts/`

## Rules
- Prefer wrapper scripts that redirect or move tool outputs into `/tmp`.
- Never leave index databases, caches, generated markdown, or temp reports in the repo unintentionally.
- Treat generated instruction files as pollution unless the user explicitly asked for them. This includes `AGENTS.md`, `CLAUDE.md`, `TOOLS.md`, `SOUL.md`, and `BOOTSTRAP.md`.
- If a tool generates instruction-file pollution, delete it or move it out of the repo before finishing.
- If the user explicitly wants in-repo docs, only the final checklist should be written there.
- Intermediate tool outputs still belong in `/tmp`.
