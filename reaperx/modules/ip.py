"""IP address intelligence: geolocation + reverse DNS.

Uses the free, key-less public endpoint http://ip-api.com/json/<ip>
(45 req/min limit). No login or scraping required.
"""

from __future__ import annotations

import ipaddress
import socket
from typing import Any

import requests

IPAPI_URL = "http://ip-api.com/json/{ip}"
DEFAULT_TIMEOUT = 8


def _validate(value: str) -> str | None:
    try:
        ipaddress.ip_address(value)
        return value
    except ValueError:
        try:
            return socket.gethostbyname(value)
        except OSError:
            return None


def _reverse_dns(ip: str) -> str | None:
    try:
        return socket.gethostbyaddr(ip)[0]
    except OSError:
        return None


def run(target: str) -> dict[str, Any]:
    target = (target or "").strip()
    if not target:
        return {"query": target, "error": "Provide an IP address or hostname."}

    ip = _validate(target)
    if ip is None:
        return {"query": target, "error": "Could not resolve as IP or hostname."}

    geo: dict[str, Any] = {}
    try:
        resp = requests.get(IPAPI_URL.format(ip=ip), timeout=DEFAULT_TIMEOUT)
        if resp.ok:
            geo = resp.json()
    except requests.RequestException as exc:
        geo = {"error": str(exc)}

    return {
        "query": target,
        "resolved_ip": ip,
        "reverse_dns": _reverse_dns(ip),
        "geo": geo,
    }
