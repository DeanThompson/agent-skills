# Authentication And Safety

Prefer `CLOUDFLARE_API_TOKEN`.

Recommended token scopes:

- `Zone:Read`
- `DNS:Read`
- `DNS:Edit`
- `Zone:Single Redirect:Edit` when managing Cloudflare redirect rules

Scope the token to only the zones that should be managed by this skill.

Legacy fallback is also supported:

- `CLOUDFLARE_EMAIL`
- `CLOUDFLARE_API_KEY`

Safety rules:

- Run `list-zones` before the first write in a new session.
- In multi-domain accounts, require `--zone-name` or `--zone-id` for writes.
- Re-list changed records after `upsert-record`, `delete-record`, or `apply-file`.
- Re-list redirect rules after `upsert-redirect`.
- For SMTP setup, verify that mail-related records are not proxied.
- For `www -> apex` routing, add a proxied DNS record first and then configure the redirect rule.
