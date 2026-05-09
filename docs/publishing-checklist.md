# Publishing Checklist

Run this checklist before publishing or pushing release changes.

## Structure

```bash
find skills -maxdepth 2 -name SKILL.md -print | sort
```

Confirm every skill directory has exactly one `SKILL.md`.

## Frontmatter

Check YAML frontmatter:

```bash
python3 scripts/validate_skills.py
```

## Runtime Wording

Runtime-specific references are allowed only when the skill explicitly handles that runtime.

```bash
rg -n "Claude|Codex|Cursor|OpenCode|CLAUDE|claude|codex" skills docs README.md AGENTS.md
```

Review every hit.

## Secrets

```bash
gitleaks detect --source . --no-git --redact
```

If `gitleaks` is not installed:

```bash
rg -n "(api[_-]?key|secret|token|password|private[_-]?key|BEGIN .*PRIVATE KEY|CLOUDFLARE_|glpat-)" .
```

Review every hit.

## Local Cruft

```bash
find . \( -name .DS_Store -o -name __pycache__ -o -name node_modules \) -print
```

The command should print nothing.

## Git

```bash
git status --short
git diff --check
```
