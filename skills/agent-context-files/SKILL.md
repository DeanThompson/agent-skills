---
name: agent-context-files
description: Create, review, and optimize persistent agent context files such as AGENTS.md, CLAUDE.md, .cursorrules, GEMINI.md, or repository-specific AI assistant instructions. Use when the user asks to create or improve agent instructions, project memory, coding-agent onboarding docs, or context files that should be loaded across sessions.
license: MIT
metadata:
  version: "0.1.0"
---

# Agent Context Files

Create concise context files that help coding agents understand a repository without flooding every session with stale or low-value instructions.

## Core Principles

1. **Less is more**: keep the always-loaded file short, ideally under 100 lines and usually under 300.
2. **Answer WHAT, WHY, and HOW**: project purpose, structure, stack, and verification commands.
3. **Use progressive disclosure**: link to detailed docs instead of copying them into the context file.
4. **Prefer pointers over snippets**: reference real files and commands that stay maintained by the project.
5. **Avoid policy duplication**: do not restate linter, formatter, or test rules that the tooling already enforces.

## Workflow

### Create A New Context File

1. Identify the target runtime or file name from the user's request.
2. Explore the repository structure and existing docs.
3. Identify the tech stack, project purpose, key directories, and common commands.
4. Draft the context file with only universal, durable information.
5. Review against the checklist below.

### Improve An Existing Context File

1. Read the current context file.
2. Identify issues: too long, stale, task-specific, runtime-specific without reason, duplicated tooling rules, or copied code snippets.
3. Move detailed material to linked docs when useful.
4. Keep or add only instructions that apply across most future agent sessions.
5. Verify the result against the checklist.

## File Selection

Use the file the user names. If the user does not specify a target:

- `AGENTS.md`: preferred portable default for multi-agent repositories.
- `CLAUDE.md`: use when the project is primarily used with Claude Code.
- `GEMINI.md`, `.cursorrules`, or other runtime-specific files: use only when requested or already established in the repo.

When a repo already has an established context file, update that file instead of creating a competing one.

## Structure Template

```markdown
# Project Name

Brief description of what this project does.

## Tech Stack

- Language/runtime
- Key frameworks
- Package manager

## Project Structure

- `src/` - Core application code
- `tests/` - Test suite
- `docs/` - Project documentation

## Development Commands

- `make test` - Run tests
- `make lint` - Run lint checks
- `make build` - Build project

## Key Patterns

- Include only non-obvious, durable conventions.
- Link to source files or docs for details.

## Additional Documentation

- `docs/architecture.md` - System architecture
- `docs/testing.md` - Test patterns and fixtures
```

## Checklist

Before finalizing, verify:

- [ ] The file is short enough to be loaded every session.
- [ ] It covers WHAT, WHY, and HOW.
- [ ] It avoids task-specific instructions.
- [ ] It avoids copied API docs or long code snippets.
- [ ] It points to maintained source files and docs.
- [ ] It does not duplicate formatter, linter, or type-checker rules.
- [ ] It uses runtime-specific language only where needed.

## References

- Read [references/best-practices.md](references/best-practices.md) for detailed context-engineering guidance.
- Read [references/examples.md](references/examples.md) for good and bad examples.
