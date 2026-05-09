# Git Worktree Reference

Create and bootstrap linked worktrees for parallel feature work.

## Usage intent

- Start code work without modifying the primary `main` or `develop` worktree.
- Create a feature branch in `.worktrees/<branch-slug>`.
- Reuse local-only environment assets when it is safe.
- Disable reuse when isolation is required.

## Decision Rules

1. Inspect current context first:
   - repository root
   - current directory
   - current branch
   - whether the current directory is a linked worktree
   - uncommitted changes
2. If the user is on `main` or `develop` and asks for code changes, prefer a linked worktree unless they explicitly want to edit in place.
3. Use `.worktrees/` under the repository root as the default parent directory.
4. Use a feature branch name from the user, or ask for one when the task needs a meaningful branch.
5. Fetch the latest remote state before creating a worktree from a remote-tracking base.
6. Do not overwrite an existing worktree path.

## Creation Flow

```bash
git status --short
git branch --show-current
git worktree list
git fetch --prune
git worktree add -b feat/example .worktrees/feat-example origin/develop
```

Replace `origin/develop` with the requested base branch. If the base branch has no remote-tracking branch, use the local base branch after confirming it is up to date enough for the task.

After creation, enter the worktree and confirm context again:

```bash
cd .worktrees/feat-example
git status --short
git branch --show-current
```

## Environment Reuse

Dependency installs and local env files can be expensive to duplicate. When the project allows it, bootstrap the new worktree by symlinking common local-only assets from the main worktree.

Use the bundled helper:

```bash
skills/git-workflow/scripts/worktree_bootstrap.sh --target .worktrees/feat-example
```

The helper links common assets when the source exists and the target path is absent:

- env files: `.env`, `.env.local`, `.env.development`, `.env.development.local`
- Python: `.venv`, `venv`
- Node.js: `node_modules`, `web/node_modules`, `frontend/node_modules`, `app/node_modules`
- Ruby/PHP: `vendor/bundle`, `vendor`
- JVM/Gradle: `.gradle`

It skips any target path that already exists as a non-symlink. It may replace existing symlinks.

## No-Reuse Mode

Use no-reuse mode when:

- the user asks for isolation
- dependencies are platform/build-output sensitive
- local env files contain task-specific settings
- multiple worktrees need different service ports or databases
- the project has no clear local-only assets to share

Command:

```bash
skills/git-workflow/scripts/worktree_bootstrap.sh --target .worktrees/feat-example --no-reuse
```

In no-reuse mode, the helper only reports the main worktree and target path, then leaves setup to the project-specific install commands.

## Service And Database Isolation

When multiple worktrees run services at the same time, do not assume they can share the same ports or database.

Common approaches:

- Share one database and run only one full stack at a time.
- Run extra worktrees on alternate ports.
- Use an isolated database only when the task needs divergent schema/data state.

Report any required port or database overrides clearly before starting services.

## Reporting

At the end, report:

- base branch and feature branch
- worktree path
- whether environment reuse was enabled or disabled
- which assets were linked or skipped
- next commands to install dependencies or start services
