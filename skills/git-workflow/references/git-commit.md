# Git Commit Reference

Create commits intelligently from the current repository state.

## Instructions

1. Analyze current changes with `git status` and `git diff` to understand modifications.
2. Group changes logically. Identify distinct areas such as frontend, backend, config, docs, and tests.
3. Create multiple focused commits when the diff clearly contains more than one logical change.
4. Use Conventional Commit format: `type(scope): description`
   - Common types: `feat`, `fix`, `refactor`, `docs`, `test`, `style`, `chore`
   - Scope should be specific
5. If a commit fails due to hooks:
   - rerun `git status`
   - re-add modified files
   - retry with the same message
   - fix any remaining hook issues if it fails again

## Commit Message Guidelines

- Use present tense and imperative mood.
- Keep the first line within 72 characters.
- Make the subject informative: include action, object, and outcome when helpful.
- Add a short body for non-trivial changes to capture why and impact.
- Reference issues or PRs in footers when relevant.
- Keep each commit focused on one logical change.

## Body Guidelines

- Prefer 2-5 short bullets or 1-2 short paragraphs.
- Focus on why the change was made, notable behavior changes, and risk or mitigation.
- If tests were run, include a `Tests:` section.
- If there are migrations or breaking changes, add `BREAKING CHANGE:` when relevant.

## Examples

- chat + dataset -> `feat(chat): ...`, `feat(dataset): ...`
- workflow + config -> `feat(workflow): ...`, `chore(config): ...`
- tests + docs -> `test: ...`, `docs: ...`

If the user gives a draft message or prefix, use it as inspiration but still analyze the actual diff before deciding commit boundaries and final wording.

