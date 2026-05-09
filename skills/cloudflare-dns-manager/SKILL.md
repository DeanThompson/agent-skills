---
name: cloudflare-dns-manager
description: Manage Cloudflare DNS zones, DNS records, and Cloudflare single redirect rules through the official API. Use when an agent needs to inspect Cloudflare zones, list DNS records, create or update SPF/DKIM/DMARC/MX/CNAME/TXT records, delete records, configure www-to-apex redirects, export zones, or prepare DNS changes for domains hosted on Cloudflare, especially when the account contains multiple zones.
license: MIT
metadata:
  author: Yangliang Li
  version: "0.1.0"
  requires:
    bins: ["python3"]
    env: ["CLOUDFLARE_API_TOKEN"]
---

# Cloudflare DNS Manager

Use the bundled script to manage Cloudflare DNS through the official API.

Prefer explicit zone selection. When multiple domains exist in the same Cloudflare account, require `--zone-name` or `--zone-id` before any write operation. Do not guess the target zone for `upsert-record`, `delete-record`, `apply-file`, or `upsert-redirect`.

## Authentication

Read [references/auth-and-safety.md](references/auth-and-safety.md) before the first write operation.

Prefer API tokens over legacy global API keys.

Supported environment variables:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_EMAIL` + `CLOUDFLARE_API_KEY`

## Workflow

### 1. Identify the zone

List available zones first:

```bash
python3 scripts/cloudflare_dns.py list-zones
```

If the user only gives a hostname and the target zone is unclear, inspect candidates:

```bash
python3 scripts/cloudflare_dns.py resolve-zone --fqdn send.example.com
```

For multi-zone accounts, stop and require an explicit `--zone-name` or `--zone-id` before editing.

### 2. Inspect existing records

List records in a zone before changing anything:

```bash
python3 scripts/cloudflare_dns.py list-records --zone-name example.com
python3 scripts/cloudflare_dns.py list-records --zone-name example.com --type TXT --name _dmarc
```

### 3. Apply the change

Create or update a single record:

```bash
python3 scripts/cloudflare_dns.py upsert-record \
  --zone-name example.com \
  --type TXT \
  --name _dmarc \
  --content 'v=DMARC1; p=none'
```

SMTP-related examples:

```bash
python3 scripts/cloudflare_dns.py upsert-record \
  --zone-name example.com \
  --type MX \
  --name send \
  --content feedback-smtp.us-east-1.amazonses.com \
  --priority 10

python3 scripts/cloudflare_dns.py upsert-record \
  --zone-name example.com \
  --type CNAME \
  --name em123._domainkey \
  --content em123.example.sendprovider.net \
  --proxied false
```

Batch apply from JSON:

```bash
python3 scripts/cloudflare_dns.py apply-file --zone-name example.com --file records.json --dry-run
python3 scripts/cloudflare_dns.py apply-file --zone-name example.com --file records.json
```

Read [references/records-json.md](references/records-json.md) for the JSON schema.

### 4. Verify the result

Re-list the affected records after any change:

```bash
python3 scripts/cloudflare_dns.py list-records --zone-name example.com --name send
```

### 5. Configure host redirects

List existing redirect rules:

```bash
python3 scripts/cloudflare_dns.py list-redirects --zone-name example.com
```

Create or update a `www -> apex` redirect:

```bash
python3 scripts/cloudflare_dns.py upsert-record \
  --zone-name example.com \
  --type CNAME \
  --name www \
  --content example.com \
  --proxied true

python3 scripts/cloudflare_dns.py upsert-redirect \
  --zone-name example.com \
  --source-host www \
  --target-host @ \
  --status-code 301 \
  --preserve-query-string true
```

Delete a redirect rule by `ref`, `id`, or source host:

```bash
python3 scripts/cloudflare_dns.py delete-redirect \
  --zone-name example.com \
  --source-host www \
  --yes
```

Export one zone for backup or migration:

```bash
python3 scripts/cloudflare_dns.py export-zone --zone-name example.com
python3 scripts/cloudflare_dns.py export-zone --zone-name example.com --file zone-export.json
```

Use redirect rules for canonical host routing. DNS alone cannot issue HTTP 301 or 302 responses.

## Guardrails

- Use `DNS only` for mail-related records. Do not proxy SMTP-related `CNAME` records.
- For `MX` records, pass `--priority`.
- For redirect rules, ensure the source hostname is proxied and the token has redirect-rule edit permission.
- For deletion, prefer `--id`. If deleting by `--name` and `--type`, include `--content` when duplicates may exist.
- Use `--dry-run` before `apply-file` on production zones.
- Stop and ask for confirmation before deleting records or redirects unless the user already explicitly requested the exact deletion.
- Keep comments and commit messages in English when editing this skill or its scripts.
