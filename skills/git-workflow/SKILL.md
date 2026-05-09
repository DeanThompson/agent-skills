---
name: git-workflow
description: Use when the user wants Git workflow help around committing, rebasing, or cleaning up branches/worktrees. Covers smart conventional commits, grouping changes into multiple focused commits, rebasing a branch onto an updated base branch, cleaning up a finished branch, removing linked git worktrees, returning to a base branch like develop, and safely deleting local branches without destructive reset operations.
license: MIT
metadata:
  author: Yangliang Li
  version: "0.1.0"
  requires:
    bins: ["git"]
---

# Git Workflow

Use this skill for three common Git tasks:

1. Smart commits for current changes
2. Rebase of the current branch onto a base branch
3. Cleanup of a finished branch or linked worktree

## Commit Workflow

Use this when the user asks to commit changes, create a good commit message, or split changes into multiple commits.

Read [references/git-commit.md](references/git-commit.md) and follow it.

Key expectations:

- Analyze actual current changes before naming commits.
- Prefer several focused commits over one large mixed commit.
- Use Conventional Commits.
- If hooks modify files or fail, re-check status, re-add files, and retry.

## Cleanup Workflow

Use this when the user asks to clean up a branch, remove a worktree, return to `develop`/`main`, or delete a finished local branch.

Read [references/git-cleanup.md](references/git-cleanup.md) and follow it.

Key expectations:

- Inspect whether the current directory is a normal worktree or linked worktree.
- Stop if there are uncommitted changes.
- Never delete the target branch.
- Only delete local branches; do not delete remotes.
- Never use destructive reset or checkout operations.

## Rebase Workflow

Use this when the user asks to rebase the current branch onto `develop`/`main`, sync a feature branch with the latest base branch, or rewrite branch history in a simple linear way.

Read [references/git-rebase.md](references/git-rebase.md) and follow it.

Key expectations:

- Inspect the current branch, target branch, and working tree state before rebasing.
- Stop if there are uncommitted changes unless the user explicitly asked for a stash-based flow.
- Prefer `git fetch --prune` before rebasing onto the latest remote-tracking target branch.
- Default to safe non-interactive rebase; only use interactive rebase when the user explicitly asks for it.
- If conflicts occur, report the conflicted files and current rebase state clearly.
