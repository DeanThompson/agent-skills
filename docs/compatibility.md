# Runtime Compatibility

This repository uses the common Agent Skills shape:

```text
skills/<skill-name>/SKILL.md
skills/<skill-name>/references/
skills/<skill-name>/scripts/
skills/<skill-name>/assets/
```

`SKILL.md` is the portable contract. The optional subdirectories are loaded or executed by agents only when needed.

## Install Locations

Common install locations include:

| Runtime | Typical location |
| --- | --- |
| Shared local skills | `~/.agents/skills` |
| Claude Code | `~/.claude/skills` or plugin-managed locations |
| Codex | `~/.codex/skills` or configured skill roots |
| Other agents | Runtime-specific skill/plugin directories |

Prefer the runtime's installer when available. If no installer exists, copy the desired skill directory into that runtime's skill directory.

## Portability Rules

- The frontmatter fields `name` and `description` are the minimum common denominator.
- Optional metadata fields may be ignored by some runtimes.
- Tool restrictions and allowed-tools fields are runtime-specific and intentionally avoided here.
- Skill bodies should say "agent" instead of assuming a specific model or vendor.
- Runtime-specific behavior belongs in documentation outside individual skill workflows.
