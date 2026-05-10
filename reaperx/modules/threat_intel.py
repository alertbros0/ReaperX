"""Aggregate keyless threat-intel signals + click-through verification links.

Uses urlscan.io's public search API (keyless, rate-limited). Generates
direct verification links to VirusTotal, URLhaus, AbuseIPDB, urlscan.io and
URLVoid so the analyst can pivot manually.
"""

from __future__ import annotations

import ipaddress
import re
import urllib.parse
from typing import Any

import requests

DEFAULT_TIMEOUT = 8
USER_AGENT = "ReaperX-OSINT/0.2"

_DOMAIN_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z]{2,})+$")


def _classify(target: str) -> str:
    try:
        ipaddress.ip_address(target)
        return "ip"
    except ValueError:
        pass
    if target.startswith("http://") or target.startswith("https://"):
        return "url"
    if _DOMAIN_RE.match(target):
        return "domain"
    return "unknown"


def _urlscan(target: str, kind: str) -> dict[str, Any]:
    if kind == "ip":
        q = f"page.ip:{target} OR ip:{target}"
    elif kind == "domain":
        q = f"page.domain:{target} OR domain:{target}"
    elif kind == "url":
        q = f"page.url:{target}"
    else:
        return {"available": False, "note": "Unknown target type."}
    try:
        r = requests.get(
            "https://urlscan.io/api/v1/search/",
            params={"q": q, "size": 10},
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            timeout=DEFAULT_TIMEOUT,
        )
    except requests.RequestException as exc:
        return {"available": False, "error": f"urlscan request failed: {exc}"}
    if r.status_code == 429:
        return {"available": False, "error": "urlscan rate-limited."}
    if not r.ok:
        return {"available": False, "error": f"urlscan HTTP {r.status_code}"}
    payload = r.json() or {}
    results = []
    for item in (payload.get("results") or [])[:10]:
        page = item.get("page") or {}
        task = item.get("task") or {}
        results.append(
            {
                "task_time": task.get("time"),
                "url": page.get("url"),
                "domain": page.get("domain"),
                "ip": page.get("ip"),
                "country": page.get("country"),
                "result": item.get("result"),
            }
        )
    return {
        "available": True,
        "total_matches": payload.get("total"),
        "scans": results,
    }


def _verification_links(target: str, kind: str) -> dict[str, str]:
    enc = urllib.parse.quote_plus(target)
    if kind == "ip":
        return {
            "VirusTotal": f"https://www.virustotal.com/gui/ip-address/{enc}",
            "AbuseIPDB": f"https://www.abuseipdb.com/check/{enc}",
            "urlscan.io": f"https://urlscan.io/ip/{enc}",
            "Shodan": f"https://www.shodan.io/host/{enc}",
            "Censys": f"https://search.censys.io/hosts/{enc}",
            "GreyNoise": f"https://viz.greynoise.io/ip/{enc}",
        }
    if kind == "domain":
        return {
            "VirusTotal": f"https://www.virustotal.com/gui/domain/{enc}",
            "URLhaus": f"https://urlhaus.abuse.ch/browse.php?search={enc}",
            "URLVoid": f"https://www.urlvoid.com/scan/{enc}/",
            "urlscan.io": f"https://urlscan.io/domain/{enc}",
            "Threatcrowd": f"https://www.threatcrowd.org/domain.php?domain={enc}",
            "crt.sh": f"https://crt.sh/?q=%25.{enc}",
        }
    if kind == "url":
        return {
            "VirusTotal": f"https://www.virustotal.com/gui/search/{enc}",
            "URLhaus": f"https://urlhaus.abuse.ch/browse.php?search={enc}",
            "URLVoid": f"https://www.urlvoid.com/scan/{enc}/",
            "urlscan.io": f"https://urlscan.io/search/#{enc}",
        }
    return {}


def run(target: str) -> dict[str, Any]:
    target = (target or "").strip()
    if not target:
        return {"error": "Target required (URL, domain, or IP)."}
    kind = _classify(target)
    if kind == "unknown":
        return {"query": target, "error": "Could not classify target as URL, domain or IP."}
    return {
        "query": target,
        "kind": kind,
        "verification_links": _verification_links(target, kind),
        "urlscan": _urlscan(target, kind),
    }
