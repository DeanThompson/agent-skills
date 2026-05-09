# Agent Skills

Small, reusable skills for coding agents.

This repository contains portable `SKILL.md`-based workflows that can be installed into runtimes such as Claude Code, Codex, Cursor, OpenCode, and other agents that support the Agent Skills convention.

## Skills

| Skill | Use when |
| --- | --- |
| [`cloudflare-dns-manager`](skills/cloudflare-dns-manager/SKILL.md) | Inspecting or changing Cloudflare DNS records, SMTP records, redirects, or zone exports. |
| [`git-workflow`](skills/git-workflow/SKILL.md) | Creating focused commits, rebasing a branch, or cleaning up local Git branches and worktrees. |
| [`gitlab-mr`](skills/gitlab-mr/SKILL.md) | Drafting, reviewing, pushing, and creating GitLab merge requests with `glab`. |
| [`agent-context-files`](skills/agent-context-files/SKILL.md) | Creating or improving persistent agent context files such as `AGENTS.md`, `CLAUDE.md`, or `.cursorrules`. |

## Install

List the available skills:

```bash
npx skills@latest add DeanThompson/agent-skills --list
```

Install interactively:

```bash
npx skills@latest add DeanThompson/agent-skills
```

Then choose the skills and target runtimes you want to install.

Install a specific skill:

```bash
npx skills@latest add DeanThompson/agent-skills --skill git-workflow
npx skills@latest add DeanThompson/agent-skills --skill cloudflare-dns-manager
npx skills@latest add DeanThompson/agent-skills --skill gitlab-mr
npx skills@latest add DeanThompson/agent-skills --skill agent-context-files
```

Install a specific skill to a specific runtime:

```bash
npx skills@latest add DeanThompson/agent-skills --skill git-workflow --agent codex -g -y
npx skills@latest add DeanThompson/agent-skills --skill git-workflow --agent claude-code -g -y
```

Install all skills:

```bash
npx skills@latest add DeanThompson/agent-skills --skill '*'
```

Manual install:

```bash
mkdir -p ~/.agents/skills
cp -R skills/cloudflare-dns-manager ~/.agents/skills/
cp -R skills/git-workflow ~/.agents/skills/
cp -R skills/gitlab-mr ~/.agents/skills/
cp -R skills/agent-context-files ~/.agents/skills/
```

Runtime-specific paths differ. See [docs/compatibility.md](docs/compatibility.md).

## Design Principles

- Keep `SKILL.md` concise and triggerable.
- Put long details in `references/` and deterministic automation in `scripts/`.
- Avoid runtime-specific assumptions in skill bodies.
- Make prerequisites explicit.
- Require confirmation or dry runs for destructive operations.

## Requirements

Individual skills may require additional tools:

- `cloudflare-dns-manager`: Python 3 and Cloudflare API credentials.
- `git-workflow`: Git.
- `gitlab-mr`: Git, GitLab CLI (`glab`), and authenticated GitLab access.
- `agent-context-files`: no external tool required beyond repository file access.

## Safety

Review any skill before installing it into an agent runtime. Skills are instructions and bundled scripts that agents may execute on your behalf.

Before publishing changes, run the checks in [docs/publishing-checklist.md](docs/publishing-checklist.md).
