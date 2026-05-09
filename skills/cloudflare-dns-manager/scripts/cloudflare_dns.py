#!/usr/bin/env python3
"""Manage Cloudflare DNS zones and records through the official API."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


API_BASE = "https://api.cloudflare.com/client/v4"
PROXYABLE_TYPES = {"A", "AAAA", "CNAME", "HTTPS"}
REDIRECT_PHASE = "http_request_dynamic_redirect"


class CloudflareError(RuntimeError):
    """Raised when the Cloudflare API returns an error."""


@dataclass
class CloudflareClient:
    api_token: str | None
    email: str | None
    api_key: str | None

    @classmethod
    def from_env(cls) -> "CloudflareClient":
        return cls(
            api_token=os.getenv("CLOUDFLARE_API_TOKEN"),
            email=os.getenv("CLOUDFLARE_EMAIL"),
            api_key=os.getenv("CLOUDFLARE_API_KEY"),
        )

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
            return headers
        if self.email and self.api_key:
            headers["X-Auth-Email"] = self.email
            headers["X-Auth-Key"] = self.api_key
            return headers
        raise CloudflareError(
            "Missing credentials. Set CLOUDFLARE_API_TOKEN or CLOUDFLARE_EMAIL with CLOUDFLARE_API_KEY."
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{API_BASE}{path}"
        if params:
            query = urllib.parse.urlencode(
                [(key, value) for key, value in params.items() if value is not None],
                doseq=True,
            )
            url = f"{url}?{query}"

        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")

        req = urllib.request.Request(url, data=data, method=method, headers=self._headers())
        try:
            with urllib.request.urlopen(req) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as json_error:
                raise CloudflareError(f"HTTP {exc.code}: {raw}") from json_error
            raise CloudflareError(self._format_error(payload)) from exc
        except urllib.error.URLError as exc:
            raise CloudflareError(f"Network error: {exc.reason}") from exc

        if not payload.get("success", False):
            raise CloudflareError(self._format_error(payload))
        return payload

    @staticmethod
    def _format_error(payload: dict[str, Any]) -> str:
        errors = payload.get("errors") or []
        if not errors:
            return "Cloudflare API returned an unknown error."
        messages = []
        for error in errors:
            code = error.get("code")
            message = error.get("message", "Unknown error")
            if code is not None:
                messages.append(f"[{code}] {message}")
            else:
                messages.append(message)
        return "; ".join(messages)


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def normalize_hostname(name: str, zone_name: str) -> str:
    trimmed = name.strip().rstrip(".")
    if trimmed in {"@", zone_name}:
        return zone_name
    if trimmed.endswith(f".{zone_name}") or trimmed == zone_name:
        return trimmed
    return f"{trimmed}.{zone_name}"


def paginate(client: CloudflareClient, path: str, *, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    merged_params = dict(params or {})
    page = 1
    per_page = int(merged_params.pop("per_page", 100))
    results: list[dict[str, Any]] = []

    while True:
        payload = client.request("GET", path, params={**merged_params, "page": page, "per_page": per_page})
        page_results = payload.get("result", [])
        results.extend(page_results)
        result_info = payload.get("result_info") or {}
        total_pages = result_info.get("total_pages", 1)
        if page >= total_pages:
            break
        page += 1

    return results


def list_zones(client: CloudflareClient, *, name: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    params = {"name": name, "status": status, "per_page": 100}
    zones = paginate(client, "/zones", params=params)
    zones.sort(key=lambda item: item["name"])
    return zones


def resolve_zone_id(client: CloudflareClient, *, zone_id: str | None, zone_name: str | None) -> tuple[str, str]:
    if zone_id:
        payload = client.request("GET", f"/zones/{zone_id}")
        zone = payload["result"]
        return zone["id"], zone["name"]

    if not zone_name:
        raise CloudflareError("Missing zone selector. Pass --zone-name or --zone-id.")

    zones = list_zones(client, name=zone_name)
    exact = [zone for zone in zones if zone["name"] == zone_name]
    if not exact:
        raise CloudflareError(f"Zone not found: {zone_name}")
    if len(exact) > 1:
        raise CloudflareError(f"Multiple zones matched {zone_name}; pass --zone-id instead.")
    zone = exact[0]
    return zone["id"], zone["name"]


def resolve_zone_candidates(client: CloudflareClient, fqdn: str) -> list[dict[str, Any]]:
    name = fqdn.strip().rstrip(".")
    zones = list_zones(client)
    candidates = []
    for zone in zones:
        zone_name = zone["name"]
        if name == zone_name or name.endswith(f".{zone_name}"):
            candidates.append(zone)
    candidates.sort(key=lambda item: (-len(item["name"]), item["name"]))
    return candidates


def list_records(
    client: CloudflareClient,
    *,
    zone_id: str,
    record_type: str | None,
    name: str | None,
    content: str | None,
) -> list[dict[str, Any]]:
    params = {"type": record_type, "name": name, "content": content, "per_page": 100}
    records = paginate(client, f"/zones/{zone_id}/dns_records", params=params)
    records.sort(key=lambda item: (item["name"], item["type"], item.get("content", "")))
    return records


def get_redirect_entrypoint(client: CloudflareClient, zone_id: str) -> dict[str, Any] | None:
    try:
        payload = client.request("GET", f"/zones/{zone_id}/rulesets/phases/{REDIRECT_PHASE}/entrypoint")
    except CloudflareError as exc:
        if "could not find entrypoint ruleset" in str(exc):
            return None
        raise
    return payload["result"]


def list_redirect_rules(client: CloudflareClient, zone_id: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    entrypoint = get_redirect_entrypoint(client, zone_id)
    if not entrypoint:
        return None, []
    rules = entrypoint.get("rules") or []
    return entrypoint, rules


def build_redirect_rule(
    source_host: str,
    target_host: str,
    *,
    description: str | None,
    status_code: int,
    preserve_query_string: bool,
) -> dict[str, Any]:
    rule_description = description or f"Redirect {source_host} to {target_host}"
    return {
        "ref": f"redirect_{source_host.replace('.', '_')}_to_{target_host.replace('.', '_')}",
        "description": rule_description,
        "expression": f'(http.host eq "{source_host}")',
        "action": "redirect",
        "action_parameters": {
            "from_value": {
                "target_url": {
                    "expression": f'concat("https://{target_host}", http.request.uri.path)',
                },
                "status_code": status_code,
                "preserve_query_string": preserve_query_string,
            }
        },
    }


def choose_existing_record(
    records: list[dict[str, Any]],
    *,
    normalized_name: str,
    record_type: str,
    content: str,
    priority: int | None = None,
) -> dict[str, Any] | None:
    exact = [record for record in records if record["name"] == normalized_name and record["type"] == record_type]
    content_match = [record for record in exact if record.get("content") == content]
    if len(content_match) == 1:
        return content_match[0]
    if len(content_match) > 1:
        raise CloudflareError(
            f"Multiple identical {record_type} records already exist for {normalized_name}. Use delete by id first."
        )
    if not exact:
        return None

    # TXT records commonly coexist on the same owner name, for example
    # a verification token and an SPF policy on the zone apex.
    if record_type == "TXT":
        return None

    # MX records can also coexist on the same owner name when priorities differ.
    if record_type == "MX":
        priority_match = [record for record in exact if record.get("priority") == priority]
        if len(priority_match) == 1 and priority_match[0].get("content") != content:
            return priority_match[0]
        if priority_match:
            return None
        return None

    if len(exact) == 1 and exact[0].get("content") != content:
        return exact[0]
    raise CloudflareError(
        f"Multiple {record_type} records already exist for {normalized_name}. Use delete by id or narrow the match."
    )


def build_record_body(args: argparse.Namespace, zone_name: str) -> dict[str, Any]:
    record_type = args.type.upper()
    body: dict[str, Any] = {
        "type": record_type,
        "name": normalize_hostname(args.name, zone_name),
        "content": args.content,
        "ttl": args.ttl,
    }

    if args.comment is not None:
        body["comment"] = args.comment

    if args.proxied is not None:
        if record_type not in PROXYABLE_TYPES:
            raise CloudflareError(f"{record_type} records do not support proxied=true/false.")
        body["proxied"] = args.proxied

    if args.priority is not None:
        body["priority"] = args.priority
    elif record_type == "MX":
        raise CloudflareError("MX records require --priority.")

    return body


def command_list_zones(args: argparse.Namespace) -> int:
    client = CloudflareClient.from_env()
    zones = list_zones(client, name=args.name, status=args.status)
    if args.json:
        print(json.dumps(zones, indent=2, ensure_ascii=False))
        return 0

    if not zones:
        print("No zones found.")
        return 0

    for zone in zones:
        account = (zone.get("account") or {}).get("name", "")
        print(f"{zone['id']}\t{zone['name']}\t{zone.get('status', '')}\t{account}")
    return 0


def command_resolve_zone(args: argparse.Namespace) -> int:
    client = CloudflareClient.from_env()
    candidates = resolve_zone_candidates(client, args.fqdn)
    if args.json:
        print(json.dumps(candidates, indent=2, ensure_ascii=False))
        return 0

    if not candidates:
        print(f"No accessible zone matches {args.fqdn}.")
        return 1

    for zone in candidates:
        print(f"{zone['id']}\t{zone['name']}\t{zone.get('status', '')}")
    return 0


def command_list_records(args: argparse.Namespace) -> int:
    client = CloudflareClient.from_env()
    zone_id, zone_name = resolve_zone_id(client, zone_id=args.zone_id, zone_name=args.zone_name)
    normalized_name = normalize_hostname(args.name, zone_name) if args.name else None
    records = list_records(
        client,
        zone_id=zone_id,
        record_type=args.type.upper() if args.type else None,
        name=normalized_name,
        content=args.content,
    )
    if args.json:
        print(json.dumps(records, indent=2, ensure_ascii=False))
        return 0

    if not records:
        print("No records found.")
        return 0

    for record in records:
        print(
            "\t".join(
                [
                    record["id"],
                    record["type"],
                    record["name"],
                    str(record.get("content", "")),
                    str(record.get("priority", "")),
                    str(record.get("ttl", "")),
                    str(record.get("proxied", "")),
                ]
            )
        )
    return 0


def command_upsert_record(args: argparse.Namespace) -> int:
    client = CloudflareClient.from_env()
    zone_id, zone_name = resolve_zone_id(client, zone_id=args.zone_id, zone_name=args.zone_name)
    body = build_record_body(args, zone_name)
    existing_records = list_records(client, zone_id=zone_id, record_type=body["type"], name=body["name"], content=None)
    existing = choose_existing_record(
        existing_records,
        normalized_name=body["name"],
        record_type=body["type"],
        content=body["content"],
        priority=body.get("priority"),
    )

    if existing:
        payload = client.request("PUT", f"/zones/{zone_id}/dns_records/{existing['id']}", body=body)
        action = "updated"
    else:
        payload = client.request("POST", f"/zones/{zone_id}/dns_records", body=body)
        action = "created"

    result = payload["result"]
    print(json.dumps({"action": action, "record": result}, indent=2, ensure_ascii=False))
    return 0


def command_delete_record(args: argparse.Namespace) -> int:
    client = CloudflareClient.from_env()
    zone_id, zone_name = resolve_zone_id(client, zone_id=args.zone_id, zone_name=args.zone_name)

    if not args.yes:
        raise CloudflareError("Refusing to delete without --yes.")

    if args.id:
        payload = client.request("DELETE", f"/zones/{zone_id}/dns_records/{args.id}")
        print(json.dumps(payload["result"], indent=2, ensure_ascii=False))
        return 0

    if not args.name or not args.type:
        raise CloudflareError("Delete by selector requires --name and --type.")

    normalized_name = normalize_hostname(args.name, zone_name)
    records = list_records(
        client,
        zone_id=zone_id,
        record_type=args.type.upper(),
        name=normalized_name,
        content=args.content,
    )

    if len(records) == 0:
        raise CloudflareError("No matching records found.")
    if len(records) > 1:
        raise CloudflareError("Multiple matching records found. Pass --id or narrow with --content.")

    payload = client.request("DELETE", f"/zones/{zone_id}/dns_records/{records[0]['id']}")
    print(json.dumps(payload["result"], indent=2, ensure_ascii=False))
    return 0


def load_records_file(path: str) -> list[dict[str, Any]]:
    raw = Path(path).read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, list):
        raise CloudflareError("Batch file must be a JSON array.")
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise CloudflareError(f"Entry #{index} must be a JSON object.")
    return data


def command_apply_file(args: argparse.Namespace) -> int:
    client = CloudflareClient.from_env()
    zone_id, zone_name = resolve_zone_id(client, zone_id=args.zone_id, zone_name=args.zone_name)
    entries = load_records_file(args.file)
    results = []

    for entry in entries:
        namespace = argparse.Namespace(
            type=entry.get("type", ""),
            name=entry.get("name", ""),
            content=entry.get("content", ""),
            ttl=entry.get("ttl", 1),
            proxied=entry.get("proxied"),
            comment=entry.get("comment"),
            priority=entry.get("priority"),
        )
        body = build_record_body(namespace, zone_name)
        existing_records = list_records(client, zone_id=zone_id, record_type=body["type"], name=body["name"], content=None)
        existing = choose_existing_record(
            existing_records,
            normalized_name=body["name"],
            record_type=body["type"],
            content=body["content"],
            priority=body.get("priority"),
        )
        action = "update" if existing else "create"
        results.append({"action": action, "record": body, "record_id": existing["id"] if existing else None})

    if args.dry_run:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    applied = []
    for result in results:
        body = result["record"]
        if result["action"] == "update":
            payload = client.request("PUT", f"/zones/{zone_id}/dns_records/{result['record_id']}", body=body)
            action = "updated"
        else:
            payload = client.request("POST", f"/zones/{zone_id}/dns_records", body=body)
            action = "created"
        applied.append({"action": action, "record": payload["result"]})

    print(json.dumps(applied, indent=2, ensure_ascii=False))
    return 0


def command_list_redirects(args: argparse.Namespace) -> int:
    client = CloudflareClient.from_env()
    zone_id, _zone_name = resolve_zone_id(client, zone_id=args.zone_id, zone_name=args.zone_name)
    entrypoint, rules = list_redirect_rules(client, zone_id)

    if args.json:
        print(json.dumps({"entrypoint": entrypoint, "rules": rules}, indent=2, ensure_ascii=False))
        return 0

    if not rules:
        print("No redirect rules found.")
        return 0

    for rule in rules:
        from_value = (rule.get("action_parameters") or {}).get("from_value") or {}
        target_expression = ((from_value.get("target_url") or {}).get("expression")) or ""
        print(
            "\t".join(
                [
                    rule.get("id", ""),
                    rule.get("ref", ""),
                    str(rule.get("enabled", True)),
                    str(from_value.get("status_code", "")),
                    rule.get("expression", ""),
                    target_expression,
                ]
            )
        )
    return 0


def command_upsert_redirect(args: argparse.Namespace) -> int:
    client = CloudflareClient.from_env()
    zone_id, zone_name = resolve_zone_id(client, zone_id=args.zone_id, zone_name=args.zone_name)
    source_host = normalize_hostname(args.source_host, zone_name)
    target_host = normalize_hostname(args.target_host, zone_name) if not args.target_host.startswith("http") else args.target_host

    if target_host.startswith("http://") or target_host.startswith("https://"):
        raise CloudflareError("Pass --target-host as a hostname without scheme.")

    new_rule = build_redirect_rule(
        source_host,
        target_host,
        description=args.description,
        status_code=args.status_code,
        preserve_query_string=args.preserve_query_string,
    )
    entrypoint, rules = list_redirect_rules(client, zone_id)

    existing_index = next(
        (
            index
            for index, rule in enumerate(rules)
            if rule.get("ref") == new_rule["ref"] or rule.get("expression") == new_rule["expression"]
        ),
        None,
    )

    if existing_index is not None:
        existing_rule = rules[existing_index]
        new_rule["id"] = existing_rule["id"]
        if existing_rule.get("ref"):
            new_rule["ref"] = existing_rule["ref"]
        rules[existing_index] = new_rule
        action = "updated"
    else:
        rules.append(new_rule)
        action = "created"

    if entrypoint is None:
        payload = client.request(
            "POST",
            "/zones/{}/rulesets".format(zone_id),
            body={
                "name": "Redirect rules ruleset",
                "description": args.ruleset_description or "Managed by cloudflare-dns-manager",
                "kind": "zone",
                "phase": REDIRECT_PHASE,
                "rules": rules,
            },
        )
    else:
        payload = client.request(
            "PUT",
            f"/zones/{zone_id}/rulesets/{entrypoint['id']}",
            body={
                "name": entrypoint["name"],
                "description": entrypoint.get("description"),
                "kind": entrypoint["kind"],
                "phase": entrypoint["phase"],
                "rules": rules,
            },
        )

    print(json.dumps({"action": action, "ruleset": payload["result"]}, indent=2, ensure_ascii=False))
    return 0


def command_delete_redirect(args: argparse.Namespace) -> int:
    client = CloudflareClient.from_env()
    zone_id, zone_name = resolve_zone_id(client, zone_id=args.zone_id, zone_name=args.zone_name)
    entrypoint, rules = list_redirect_rules(client, zone_id)

    if not entrypoint or not rules:
        raise CloudflareError("No redirect rules found.")

    if not args.yes:
        raise CloudflareError("Refusing to delete redirect without --yes.")

    source_host = normalize_hostname(args.source_host, zone_name) if args.source_host else None
    expression = f'(http.host eq "{source_host}")' if source_host else None

    matches = []
    for rule in rules:
        if args.id and rule.get("id") == args.id:
            matches.append(rule)
            continue
        if args.ref and rule.get("ref") == args.ref:
            matches.append(rule)
            continue
        if expression and rule.get("expression") == expression:
            matches.append(rule)

    if not matches:
        raise CloudflareError("No matching redirect rule found.")
    if len(matches) > 1:
        raise CloudflareError("Multiple matching redirect rules found. Pass --id or --ref.")

    target_id = matches[0]["id"]
    updated_rules = [rule for rule in rules if rule.get("id") != target_id]

    payload = client.request(
        "PUT",
        f"/zones/{zone_id}/rulesets/{entrypoint['id']}",
        body={
            "name": entrypoint["name"],
            "description": entrypoint.get("description"),
            "kind": entrypoint["kind"],
            "phase": entrypoint["phase"],
            "rules": updated_rules,
        },
    )
    print(json.dumps({"action": "deleted", "ruleset": payload["result"]}, indent=2, ensure_ascii=False))
    return 0


def command_export_zone(args: argparse.Namespace) -> int:
    client = CloudflareClient.from_env()
    zone_id, _zone_name = resolve_zone_id(client, zone_id=args.zone_id, zone_name=args.zone_name)
    zone_payload = client.request("GET", f"/zones/{zone_id}")
    zone = zone_payload["result"]
    records = list_records(client, zone_id=zone_id, record_type=None, name=None, content=None)
    entrypoint, redirects = list_redirect_rules(client, zone_id)

    export_data = {
        "zone": {
            "id": zone["id"],
            "name": zone["name"],
            "status": zone.get("status"),
            "account": zone.get("account"),
            "name_servers": zone.get("name_servers"),
        },
        "dns_records": records,
        "redirect_rules": {
            "entrypoint": entrypoint,
            "rules": redirects,
        },
    }

    rendered = json.dumps(export_data, indent=2, ensure_ascii=False)
    if args.file:
        Path(args.file).write_text(rendered + "\n", encoding="utf-8")
        print(args.file)
        return 0

    print(rendered)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_zones_parser = subparsers.add_parser("list-zones", help="List accessible zones")
    list_zones_parser.add_argument("--name", help="Filter by exact zone name")
    list_zones_parser.add_argument("--status", help="Filter by zone status")
    list_zones_parser.add_argument("--json", action="store_true", help="Print JSON output")
    list_zones_parser.set_defaults(func=command_list_zones)

    resolve_zone_parser = subparsers.add_parser("resolve-zone", help="Find matching zones for a hostname")
    resolve_zone_parser.add_argument("--fqdn", required=True, help="Hostname to match against accessible zones")
    resolve_zone_parser.add_argument("--json", action="store_true", help="Print JSON output")
    resolve_zone_parser.set_defaults(func=command_resolve_zone)

    list_records_parser = subparsers.add_parser("list-records", help="List records in a zone")
    add_zone_args(list_records_parser)
    list_records_parser.add_argument("--type", help="Record type filter, such as TXT or MX")
    list_records_parser.add_argument("--name", help="Record name, relative label, @, or full hostname")
    list_records_parser.add_argument("--content", help="Record content filter")
    list_records_parser.add_argument("--json", action="store_true", help="Print JSON output")
    list_records_parser.set_defaults(func=command_list_records)

    upsert_parser = subparsers.add_parser("upsert-record", help="Create or update one record")
    add_zone_args(upsert_parser)
    add_record_args(upsert_parser)
    upsert_parser.set_defaults(func=command_upsert_record)

    delete_parser = subparsers.add_parser("delete-record", help="Delete one record")
    add_zone_args(delete_parser)
    delete_parser.add_argument("--id", help="Record id")
    delete_parser.add_argument("--type", help="Record type when deleting by selector")
    delete_parser.add_argument("--name", help="Record name when deleting by selector")
    delete_parser.add_argument("--content", help="Optional content filter when deleting by selector")
    delete_parser.add_argument("--yes", action="store_true", help="Confirm deletion")
    delete_parser.set_defaults(func=command_delete_record)

    apply_file_parser = subparsers.add_parser("apply-file", help="Batch create or update records from JSON")
    add_zone_args(apply_file_parser)
    apply_file_parser.add_argument("--file", required=True, help="Path to a JSON array of record definitions")
    apply_file_parser.add_argument("--dry-run", action="store_true", help="Show planned actions without writing")
    apply_file_parser.set_defaults(func=command_apply_file)

    list_redirects_parser = subparsers.add_parser("list-redirects", help="List Cloudflare single redirect rules")
    add_zone_args(list_redirects_parser)
    list_redirects_parser.add_argument("--json", action="store_true", help="Print JSON output")
    list_redirects_parser.set_defaults(func=command_list_redirects)

    upsert_redirect_parser = subparsers.add_parser("upsert-redirect", help="Create or update one host redirect rule")
    add_zone_args(upsert_redirect_parser)
    upsert_redirect_parser.add_argument("--source-host", required=True, help="Source hostname, relative label, @, or full hostname")
    upsert_redirect_parser.add_argument("--target-host", required=True, help="Target hostname without scheme")
    upsert_redirect_parser.add_argument("--status-code", type=int, default=301, choices=[301, 302, 307, 308])
    upsert_redirect_parser.add_argument(
        "--preserve-query-string",
        type=parse_bool,
        default=True,
        help="Whether to preserve the original query string",
    )
    upsert_redirect_parser.add_argument("--description", help="Optional rule description")
    upsert_redirect_parser.add_argument("--ruleset-description", help="Description used when creating a new ruleset")
    upsert_redirect_parser.set_defaults(func=command_upsert_redirect)

    delete_redirect_parser = subparsers.add_parser("delete-redirect", help="Delete one host redirect rule")
    add_zone_args(delete_redirect_parser)
    delete_redirect_parser.add_argument("--id", help="Redirect rule id")
    delete_redirect_parser.add_argument("--ref", help="Redirect rule ref")
    delete_redirect_parser.add_argument("--source-host", help="Source hostname, relative label, @, or full hostname")
    delete_redirect_parser.add_argument("--yes", action="store_true", help="Confirm deletion")
    delete_redirect_parser.set_defaults(func=command_delete_redirect)

    export_zone_parser = subparsers.add_parser("export-zone", help="Export zone metadata, DNS records, and redirect rules")
    add_zone_args(export_zone_parser)
    export_zone_parser.add_argument("--file", help="Write JSON export to a file instead of stdout")
    export_zone_parser.set_defaults(func=command_export_zone)

    return parser


def add_zone_args(parser: argparse.ArgumentParser) -> None:
    zone_group = parser.add_mutually_exclusive_group(required=True)
    zone_group.add_argument("--zone-name", help="Cloudflare zone name, such as example.com")
    zone_group.add_argument("--zone-id", help="Cloudflare zone id")


def add_record_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--type", required=True, help="Record type, such as TXT, CNAME, or MX")
    parser.add_argument("--name", required=True, help="Record name, relative label, @, or full hostname")
    parser.add_argument("--content", required=True, help="Record content")
    parser.add_argument("--ttl", type=int, default=1, help="TTL in seconds, or 1 for automatic")
    parser.add_argument("--proxied", type=parse_bool, help="Whether the record should be proxied")
    parser.add_argument("--comment", help="Optional comment")
    parser.add_argument("--priority", type=int, help="Priority, required for MX")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except CloudflareError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
