# Batch JSON Format

`apply-file` accepts a JSON array. Each item maps to one `upsert-record` operation.

Example:

```json
[
  {
    "type": "TXT",
    "name": "@",
    "content": "v=spf1 include:amazonses.com ~all",
    "ttl": 1,
    "comment": "SPF for SES"
  },
  {
    "type": "TXT",
    "name": "_dmarc",
    "content": "v=DMARC1; p=none; rua=mailto:dmarc@example.com",
    "ttl": 1
  },
  {
    "type": "CNAME",
    "name": "selector1._domainkey",
    "content": "selector1-example-com._domainkey.provider.example",
    "proxied": false,
    "ttl": 1
  },
  {
    "type": "MX",
    "name": "send",
    "content": "feedback-smtp.us-east-1.amazonses.com",
    "priority": 10,
    "ttl": 1
  }
]
```

Supported fields:

- `type`
- `name`
- `content`
- `ttl`
- `proxied`
- `comment`
- `priority`

Notes:

- `name` can be `@`, a relative label like `_dmarc`, or a full hostname.
- `priority` is required for `MX`.
- `proxied` is only valid for proxyable record types such as `A`, `AAAA`, and `CNAME`.
