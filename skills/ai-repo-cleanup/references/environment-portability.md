# Environment and Portability

## Default execution model
- Prefer system `python3` and basic shell tools.
- Do not require a virtual environment for the default audit path.
- Do not require package installation before running audit scripts.

## Script rules
- Scripts should be stdlib-only when possible.
- Scripts should not import the target repository's code.
- Scripts should emit stable JSON and avoid side effects outside `/tmp/skill/ai-repo-cleanup/...`.

## Optional environments
- If a stronger tool depends on a project environment, treat it as optional.
- Let the agent decide whether entering an existing venv or repo environment is worth it.
- Do not create or install environments by default.

## Failure handling
- If `python3` is unavailable, fall back to shell-only evidence where possible.
- If optional tools are unavailable, continue and mark unresolved areas `needs-proof`.
