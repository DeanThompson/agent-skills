---
name: gitlab-mr
description: Use when the user wants to create a GitLab merge request, draft an MR title and description, compare the current branch against a target branch, push the branch, or run `glab mr create`. Covers previewing the generated MR copy and confirming before creation.
license: MIT
metadata:
  version: "0.1.0"
  requires:
    bins: ["git", "glab"]
---

# GitLab MR

Use this skill when the user wants to open or draft a GitLab merge request.

Read [references/gitlab-mr.md](references/gitlab-mr.md) and follow it.

Key expectations:

- Check for uncommitted changes before creating the MR.
- Confirm `glab auth status` succeeds before attempting to create the MR.
- Compare the current branch against the target branch, defaulting to `develop`.
- Generate a conventional-commit-style MR title.
- Draft a concise MR description with review-friendly sections.
- Show a preview and get confirmation before running `glab mr create`.
