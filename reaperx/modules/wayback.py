"""Wayback Machine snapshot lookup via the public CDX API."""

from __future__ import annotations

from typing import Any

import requests

CDX_URL = "https://web.archive.org/cdx/search/cdx"
USER_AGENT = "ReaperX/0.1 OSINT-research-tool"
DEFAULT_TIMEOUT = 20


def run(url: str, limit: int = 50) -> dict[str, Any]:
    url = (url or "").strip()
    if not url:
        return {"query": url, "error": "Provide a URL or domain."}

    params = {
        "url": url,
        "output": "json",
        "limit": str(limit),
        "fl": "timestamp,original,statuscode,mimetype",
        "filter": "statuscode:200",
        "collapse": "timestamp:8",
    }
    try:
        resp = requests.get(
            CDX_URL,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=DEFAULT_TIMEOUT,
        )
    except requests.RequestException as exc:
        return {"query": url, "error": f"Wayback request failed: {exc}"}

    if not resp.ok:
        return {"query": url, "error": f"Wayback returned HTTP {resp.status_code}"}

    try:
        rows = resp.json()
    except ValueError:
        return {"query": url, "error": "Wayback returned non-JSON."}

    if not rows or len(rows) < 2:
        return {"query": url, "snapshots": [], "count": 0}

    header, *data = rows
    snapshots = []
    for row in data:
        record = dict(zip(header, row, strict=False))
        ts = record.get("timestamp", "")
        record["snapshot_url"] = f"https://web.archive.org/web/{ts}/{record.get('original', '')}"
        snapshots.append(record)

    return {"query": url, "count": len(snapshots), "snapshots": snapshots}
