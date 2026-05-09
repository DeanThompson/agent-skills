# Git Rebase Reference

Rebase the current branch onto an updated base branch such as `develop` or `main`.
Prefer a safe, linear workflow that updates the branch without merge commits.

## Usage intent

- Rebase the current feature branch onto `develop`
- Rebase the current feature branch onto `main`
- Sync the branch with the latest base branch before opening or updating a PR
- Perform a simple history rewrite without using merge

## Instructions

1. Resolve the target branch from the user's request, or use `develop` if not provided.
2. Inspect the repository state before making changes:
   - get the current branch name
   - confirm the current directory belongs to the expected repository
   - check for uncommitted changes with `git status --short`
   - detect whether the branch is in the middle of an existing rebase
3. If there are uncommitted changes, stop and warn the user instead of rebasing, unless the user explicitly asked for a stash-based workflow.
4. Fetch the latest remote state before rebasing:
   - run `git fetch --prune`
   - prefer rebasing onto the remote-tracking branch such as `origin/develop` or `origin/main`
5. By default, use a non-interactive rebase of the current branch onto the target branch.
6. Only use interactive rebase when the user explicitly asks to squash, reorder, edit, or drop commits.
7. If conflicts occur during rebase:
   - inspect `git status`
   - identify the conflicted files
   - resolve only the conflicts that are clear from local context
   - stage resolved files and continue with `git rebase --continue`
   - if the correct resolution is ambiguous, stop and report the conflict instead of guessing
8. If the user asks to stop or discard the in-progress rebase, use `git rebase --abort`.
9. At the end, report:
   - original branch
   - target branch
   - whether the rebase completed successfully
   - whether conflicts occurred and how they were handled
   - whether a force push is likely needed to update the remote branch

## Important behavior

- Never start a rebase on top of uncommitted local changes unless the user explicitly wants that behavior.
- Never use destructive reset or checkout operations as a shortcut for resolving rebase issues.
- Prefer `git rebase origin/<target>` over rebasing onto a potentially stale local target branch.
- After a successful rebase of a branch that already exists on the remote, explain that pushing will usually require `git push --force-with-lease`.
- Do not push automatically unless the user explicitly asks for it.
