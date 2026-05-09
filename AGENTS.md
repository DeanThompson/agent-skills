# Agent Instructions

This repo is a public skill pack. Keep changes portable across agent runtimes.

## Conventions

- Put installable skills under `skills/<skill-name>/`.
- Every skill must include `SKILL.md` with YAML frontmatter containing at least `name` and `description`.
- Keep `SKILL.md` focused on the core workflow and trigger guidance.
- Move longer details to `references/`.
- Put deterministic helper code in `scripts/`.
- Do not add per-skill README files unless a runtime explicitly requires them.
- Prefer ASCII in docs and scripts unless the source skill is intentionally Chinese-language.

## Compatibility

- Do not assume a specific runtime in skill bodies.
- Use "agent" or "runtime" unless a section is intentionally runtime-specific.
- Keep runtime-specific install notes in `docs/compatibility.md`.
- Avoid runtime-specific frontmatter fields unless they are optional metadata.

## Safety

- Do not commit secrets, local caches, `.DS_Store`, `node_modules`, or `__pycache__`.
- Preserve destructive-operation guardrails.
- For CLI-backed skills, document prerequisites, authentication, and confirmation behavior.
- Run the publishing checklist before committing release changes.
