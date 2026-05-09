---
name: git-workflow
description: Use when the user wants Git workflow help around committing, rebasing, creating linked worktrees, bootstrapping a worktree environment, or cleaning up branches/worktrees. Covers smart conventional commits, grouping changes into focused commits, safe rebases, linked worktree setup under .worktrees, optional environment reuse through symlinks, branch cleanup, and safe local branch deletion without destructive reset operations.
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
3. Linked worktree creation and environment bootstrap
4. Cleanup of a finished branch or linked worktree

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

## Worktree Workflow

Use this when the user asks to create a linked worktree, start feature work away from `main`/`develop`, or bootstrap a worktree environment.

Read [references/git-worktree.md](references/git-worktree.md) and follow it.

Key expectations:

- Confirm the repository root, current branch, linked-worktree status, and uncommitted changes before creating or entering a worktree.
- Prefer linked worktrees under the repository root at `.worktrees/<branch-slug>`.
- Prefer creating a feature branch from the requested base branch rather than editing directly on `main` or `develop`.
- Offer environment reuse by symlinking common local-only assets from the main worktree.
- Respect a no-reuse option when the user wants isolation or the project cannot safely share dependencies.
- Never overwrite existing non-symlink files while bootstrapping.

## Rebase Workflow

Use this when the user asks to rebase the current branch onto `develop`/`main`, sync a feature branch with the latest base branch, or rewrite branch history in a simple linear way.

Read [references/git-rebase.md](references/git-rebase.md) and follow it.

Key expectations:

- Inspect the current branch, target branch, and working tree state before rebasing.
- Stop if there are uncommitted changes unless the user explicitly asked for a stash-based flow.
- Prefer `git fetch --prune` before rebasing onto the latest remote-tracking target branch.
- Default to safe non-interactive rebase; only use interactive rebase when the user explicitly asks for it.
- If conflicts occur, report the conflicted files and current rebase state clearly.
