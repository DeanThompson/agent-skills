# Agent Context File Examples

## Good Example

```markdown
# MyApp

E-commerce platform built with Next.js and PostgreSQL.

## Tech Stack

- Node 20, pnpm
- Next.js App Router
- PostgreSQL, Prisma ORM
- Tailwind CSS

## Structure

- `src/app/` - routes and API handlers
- `src/components/` - reusable UI
- `src/lib/` - shared utilities
- `prisma/` - schema and migrations

## Commands

- `pnpm dev` - start the dev server
- `pnpm test` - run tests
- `pnpm lint` - run lint checks
- `pnpm db:migrate` - run migrations

## Key Patterns

- Server components by default; use client components only for interactivity.
- Database access goes through `src/lib/db.ts`.

## Docs

- `docs/api.md` - API endpoint overview
- `docs/database.md` - schema notes and migration workflow
```

Why it works:

- Short enough to load every session.
- Covers WHAT, WHY, and HOW.
- Uses pointers instead of copied docs.
- Includes only durable conventions.

## Bad Example

```markdown
# MyApp

[50 lines of project history]

## Code Style

- Use 2 spaces for indentation.
- Always use semicolons.
- Prefer const over let.
- Use arrow functions.
[100 more style rules]

## How To Add A New API Endpoint

1. Create a file in `src/app/api/`.
2. Export async function GET/POST.
3. Add validation with zod.
[50 more lines]

## Example: User Authentication

[100-line code example]
```

Why it fails:

- Code style belongs in tooling.
- Task-specific workflows should be separate docs.
- Long code examples become stale.
- The file is too noisy to be reliably useful.

## Transformation Example

Before:

```markdown
## API Response Format

Always return responses in this format:

{
  "success": true,
  "data": {},
  "error": null
}
```

After:

```markdown
## API Patterns

Response helpers live in `src/lib/api/response.ts`.
```
