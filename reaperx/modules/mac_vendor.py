"""MAC address OUI vendor lookup using the keyless maclookup.app API."""

from __future__ import annotations

import re
from typing import Any

import requests

DEFAULT_TIMEOUT = 8
USER_AGENT = "ReaperX-OSINT/0.2"

_HEX_PAIR = re.compile(r"([0-9A-Fa-f]{2})")


def _normalize(mac: str) -> str | None:
    pairs = _HEX_PAIR.findall(mac or "")
    if len(pairs) < 3:
        return None
    pairs = pairs[:6] if len(pairs) >= 6 else pairs[:3]
    return ":".join(p.upper() for p in pairs)


def run(mac: str) -> dict[str, Any]:
    raw = (mac or "").strip()
    if not raw:
        return {"error": "MAC address required."}
    normalized = _normalize(raw)
    if not normalized:
        return {"query": raw, "error": "Invalid MAC address (need at least 3 hex pairs)."}
    oui = ":".join(normalized.split(":")[:3])
    try:
        r = requests.get(
            f"https://api.maclookup.app/v2/macs/{oui}",
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            timeout=DEFAULT_TIMEOUT,
        )
    except requests.RequestException as exc:
        return {"query": raw, "normalized": normalized, "oui": oui, "error": f"Lookup failed: {exc}"}
    if not r.ok:
        return {
            "query": raw,
            "normalized": normalized,
            "oui": oui,
            "error": f"Lookup failed: HTTP {r.status_code}",
        }
    data = r.json() or {}
    found = bool(data.get("found"))
    return {
        "query": raw,
        "normalized": normalized,
        "oui": oui,
        "found": found,
        "company": data.get("company"),
        "address": data.get("address"),
        "country": data.get("country"),
        "block_type": data.get("blockType"),
        "is_random": data.get("isRand"),
        "updated": data.get("updated"),
    }
