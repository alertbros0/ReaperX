"""Multi-resolver DNS-over-HTTPS lookup (Cloudflare, Google, Quad9)."""

from __future__ import annotations

import concurrent.futures as cf
from typing import Any

import requests

DEFAULT_TIMEOUT = 6
USER_AGENT = "ReaperX-OSINT/0.2"

RESOLVERS = {
    "Cloudflare (1.1.1.1)": "https://cloudflare-dns.com/dns-query",
    "Google (8.8.8.8)": "https://dns.google/resolve",
    "Quad9 (9.9.9.9)": "https://dns.quad9.net:5053/dns-query",
}

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]


def _query(resolver_url: str, name: str, rtype: str) -> list[str]:
    try:
        r = requests.get(
            resolver_url,
            params={"name": name, "type": rtype},
            headers={"Accept": "application/dns-json", "User-Agent": USER_AGENT},
            timeout=DEFAULT_TIMEOUT,
        )
        if not r.ok:
            return []
        payload = r.json() or {}
        answers = payload.get("Answer") or []
        return [str(a.get("data")).strip().strip('"') for a in answers if a.get("data")]
    except (requests.RequestException, ValueError):
        return []


def _resolver_block(resolver_name: str, resolver_url: str, name: str) -> dict[str, Any]:
    records: dict[str, list[str]] = {}
    with cf.ThreadPoolExecutor(max_workers=len(RECORD_TYPES)) as pool:
        futures = {
            pool.submit(_query, resolver_url, name, rtype): rtype for rtype in RECORD_TYPES
        }
        for fut in cf.as_completed(futures):
            rtype = futures[fut]
            records[rtype] = fut.result()
    total = sum(len(v) for v in records.values())
    return {"resolver": resolver_name, "records": records, "answer_count": total}


def run(host: str) -> dict[str, Any]:
    host = (host or "").strip().rstrip(".")
    if not host:
        return {"error": "Host required."}
    resolvers: list[dict[str, Any]] = []
    with cf.ThreadPoolExecutor(max_workers=len(RESOLVERS)) as pool:
        futures = {
            pool.submit(_resolver_block, name, url, host): name
            for name, url in RESOLVERS.items()
        }
        for fut in cf.as_completed(futures):
            resolvers.append(fut.result())
    resolvers.sort(key=lambda r: r["resolver"])
    return {
        "query": host,
        "resolver_count": len(resolvers),
        "resolvers": resolvers,
    }
