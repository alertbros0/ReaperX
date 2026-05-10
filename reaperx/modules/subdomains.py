"""Passive subdomain enumeration via crt.sh certificate-transparency logs."""

from __future__ import annotations

from typing import Any

import requests

CRTSH_URL = "https://crt.sh/?q=%25.{domain}&output=json"
USER_AGENT = "ReaperX/0.1 OSINT-research-tool"
DEFAULT_TIMEOUT = 30


def run(domain: str, limit: int = 500) -> dict[str, Any]:
    domain = (domain or "").strip().lower().lstrip("*.")
    if not domain or "." not in domain:
        return {"query": domain, "error": "Provide a fully-qualified domain name."}

    try:
        resp = requests.get(
            CRTSH_URL.format(domain=domain),
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            timeout=DEFAULT_TIMEOUT,
        )
    except requests.RequestException as exc:
        return {"query": domain, "error": f"crt.sh request failed: {exc}"}

    if not resp.ok:
        return {"query": domain, "error": f"crt.sh returned HTTP {resp.status_code}"}

    try:
        rows = resp.json()
    except ValueError:
        return {"query": domain, "error": "crt.sh returned non-JSON (try again later)."}

    found: set[str] = set()
    for row in rows:
        name = row.get("name_value", "")
        for sub in name.splitlines():
            sub = sub.strip().lower().lstrip("*.")
            if sub.endswith(domain):
                found.add(sub)

    sorted_subs = sorted(found)
    return {
        "query": domain,
        "count": len(sorted_subs),
        "subdomains": sorted_subs[:limit],
        "truncated": len(sorted_subs) > limit,
    }
