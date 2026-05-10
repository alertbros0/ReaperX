"""Username search across public social/dev platforms.

For each known site we issue a single GET request to the public profile URL
and decide whether the account *probably* exists based on:

  * HTTP status code (404 → absent)
  * a configurable "absent" marker string in the response body

We never log in, never bypass rate limits, and never scrape private content.
"""

from __future__ import annotations

import concurrent.futures as cf
import json
import re
from importlib import resources
from typing import Any

import requests

USER_AGENT = (
    "ReaperX/0.1 (+https://github.com/alertbros0/ReaperX) "
    "OSINT-research-tool"
)
DEFAULT_TIMEOUT = 8
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.\-]{1,39}$")


def _load_sites() -> dict[str, dict[str, Any]]:
    raw = resources.files("reaperx.data").joinpath("sites.json").read_text(encoding="utf-8")
    return json.loads(raw)


def _check(name: str, spec: dict[str, Any], username: str) -> dict[str, Any]:
    url = spec["url"].format(u=username)
    absent_marker: str | None = spec.get("absent")
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"},
            timeout=DEFAULT_TIMEOUT,
            allow_redirects=True,
        )
    except requests.RequestException as exc:
        return {"site": name, "url": url, "status": "error", "error": str(exc)}

    if resp.status_code == 404:
        verdict = "absent"
    elif resp.status_code >= 400:
        verdict = "unknown"
    elif absent_marker and absent_marker.lower() in resp.text.lower():
        verdict = "absent"
    else:
        verdict = "present"

    return {
        "site": name,
        "url": url,
        "status": verdict,
        "http_status": resp.status_code,
    }


def run(username: str, max_workers: int = 12) -> dict[str, Any]:
    """Look up `username` across all configured sites.

    Returns a dict with ``query``, ``hits`` (list of present sites), and
    ``checks`` (full per-site results).
    """
    if not username or not USERNAME_RE.match(username):
        return {
            "query": username,
            "error": "Invalid username. Allowed: letters, digits, _ . - (max 39 chars)",
            "hits": [],
            "checks": [],
        }

    sites = _load_sites()
    results: list[dict[str, Any]] = []
    with cf.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_check, name, spec, username): name for name, spec in sites.items()}
        for fut in cf.as_completed(futures):
            results.append(fut.result())

    results.sort(key=lambda r: r["site"].lower())
    hits = [r for r in results if r["status"] == "present"]
    return {
        "query": username,
        "total_sites": len(results),
        "found": len(hits),
        "hits": hits,
        "checks": results,
    }
