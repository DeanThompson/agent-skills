# GitLab MR Reference

Analyze changes between the current branch and the target branch, generate an MR title and description, then push and create the MR using `glab mr create`.

## Requirements

1. Check for uncommitted changes first; warn the user if any exist.
2. Confirm `glab auth status` succeeds before creating an MR.
3. Generate the title with Conventional Commit format: `type(scope): description`.
4. Draft a concise description with these sections:
   - Summary
   - Motivation
   - Changes
   - Testing
   - Risk
   - Checklist
5. Show a preview and confirm with the user before creating the MR.
6. Use a HEREDOC for the multi-line description.
7. Avoid the `--web` flag.

## Suggested Flow

```bash
git status --short
git branch --show-current
git fetch --prune
git diff --stat origin/develop...HEAD
git diff origin/develop...HEAD
glab auth status
```

Replace `develop` with the requested target branch when needed.

After preview and confirmation:

```bash
git push -u origin HEAD
glab mr create --target-branch develop --source-branch "$(git branch --show-current)" --title "..." --description "$(cat <<'DESC'
...
DESC
)"
```

## Target Branch

- Default target branch is `develop` if the user does not specify one.

## Description Guidance

- Summary: 1-2 sentences on what the MR delivers.
- Motivation: Why now; problem or opportunity; link context if needed.
- Changes: 2-6 bullets focused on notable, reviewable items.
- Testing: List commands; use `Not run` if no tests were executed.
- Risk: Low, Medium, or High with a brief reason and any mitigation.
- Checklist: Simple checkboxes; include docs, migration, and backward-compatibility when relevant.
