# Git Cleanup Reference

Clean up the current Git workspace and return to a base branch (default: `develop`).
Support both normal working trees and linked `git worktree` directories.

## Usage intent

- Return to `develop`, update it, and clean up the current branch/worktree
- Keep another base branch such as `main` instead of `develop`

## Instructions

1. Resolve the target branch from the user's request, or use `develop` if not provided.
2. Inspect the current repository state before making changes:
   - get the current branch name
   - detect whether the current directory is the main worktree or a linked `git worktree`
   - list worktrees when needed to understand which path owns the current branch
   - check for uncommitted changes in the current worktree
3. If the current worktree has uncommitted changes, stop and warn the user instead of cleaning anything up.
4. If the current directory is a normal worktree:
   - switch to the target branch if needed
   - fetch/prune and fast-forward pull the target branch
   - delete the previous local branch if it is different from the target branch
5. If the current directory is a linked worktree:
   - identify the main worktree path for the same repository
   - from the main worktree, fetch/prune and fast-forward pull the target branch
   - remove the linked worktree path with `git worktree remove`
   - delete the local branch that belonged to the removed worktree if it is different from the target branch
   - if the remote branch was already deleted, treat that as success rather than failure
6. Never delete the target branch.
7. Never use destructive reset/checkout operations.
8. At the end, report:
   - original branch
   - whether the cleanup was for a normal worktree or linked worktree
   - target branch and updated commit
   - whether the local branch was deleted
   - whether the remote branch still existed or was already gone

If the current branch is already the target branch in a normal worktree, just update it and skip branch deletion.

Important behavior:

- Prefer `git fetch --prune` before checking remote branch state.
- Prefer `git pull --ff-only` when updating the target branch.
- Only delete local branches. Do not delete the remote branch.

