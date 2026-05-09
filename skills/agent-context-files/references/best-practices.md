# Agent Context File Best Practices

## Why Context Files Matter

Agent context files are loaded into future sessions to orient the agent. They are high-leverage because a good instruction helps every task, while a bad instruction creates repeated bad behavior.

Common file names include:

- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `.cursorrules`
- Runtime-specific project instruction files

## The Three Questions

Every context file should answer:

1. **WHAT**: tech stack, project structure, and key directories.
2. **WHY**: project purpose and important design constraints.
3. **HOW**: commands to build, test, lint, run, and verify changes.

## Instruction Limits

Frontier coding agents already receive large system prompts. Project context should be additive, not repetitive.

Guidelines:

- Keep the always-loaded context under 300 lines.
- Prefer under 100 lines for ordinary repositories.
- Remove instructions that apply only to one narrow task.
- Remove formatting rules when the repo has a formatter or linter.
- Remove content that can be discovered quickly from standard files.

## Progressive Disclosure

Use the main context file as an index:

```text
agent_docs/
  architecture.md
  testing.md
  deployment.md
  database-schema.md
```

Then link only the relevant docs:

```markdown
## Additional Documentation

- `agent_docs/architecture.md` - service boundaries and data flow
- `agent_docs/testing.md` - fixtures and integration test setup
- `agent_docs/deployment.md` - release and rollback procedure
```

The agent reads detailed docs only when the task needs them.

## What To Avoid

- Full API documentation copied into the context file.
- Long code examples that will drift from implementation.
- Personal preferences unrelated to the repository.
- Duplicated linter, formatter, or type-checker configuration.
- Stale project history.
- Instructions that conflict with runtime/system instructions.

## Good Pointers

Use pointers to maintained sources:

- `src/lib/api/response.ts` for response shape.
- `docs/architecture.md` for service boundaries.
- `Makefile` or `package.json` scripts for commands.

Avoid copying code snippets unless the snippet is tiny, stable, and more useful than a pointer.
