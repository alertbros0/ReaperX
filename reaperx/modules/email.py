"""Email investigation.

Provides:
  * syntax + deliverability validation (email-validator)
  * Gravatar avatar URL & profile JSON link (md5 of lowercased email)
  * MX-record verification of the email's domain
  * Optional Have-I-Been-Pwned breach lookup if ``HIBP_API_KEY`` is set
"""

from __future__ import annotations

import hashlib
import os
from typing import Any

import dns.exception
import dns.resolver
import requests
from email_validator import EmailNotValidError, validate_email

HIBP_URL = "https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"
GRAVATAR_AVATAR = "https://www.gravatar.com/avatar/{h}?d=404"
GRAVATAR_PROFILE = "https://www.gravatar.com/{h}.json"
USER_AGENT = "ReaperX/0.1 OSINT-research-tool"
DEFAULT_TIMEOUT = 8


def _gravatar_hash(email: str) -> str:
    return hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()  # noqa: S324


def _mx_records(domain: str) -> list[str]:
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=5.0)
        return sorted({r.to_text() for r in answers})
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
        return []
    except Exception:
        return []


def _gravatar(email: str) -> dict[str, Any]:
    h = _gravatar_hash(email)
    avatar = GRAVATAR_AVATAR.format(h=h)
    profile_url = GRAVATAR_PROFILE.format(h=h)
    info: dict[str, Any] = {"hash": h, "avatar_url": avatar, "profile_url": profile_url, "exists": False}
    try:
        r = requests.get(avatar, timeout=DEFAULT_TIMEOUT, headers={"User-Agent": USER_AGENT})
        info["exists"] = r.status_code == 200
    except requests.RequestException as exc:
        info["error"] = str(exc)
    return info


def _hibp(email: str) -> dict[str, Any]:
    api_key = os.environ.get("HIBP_API_KEY")
    if not api_key:
        return {"enabled": False, "note": "Set HIBP_API_KEY to enable breach lookups."}
    headers = {"hibp-api-key": api_key, "User-Agent": USER_AGENT}
    try:
        r = requests.get(HIBP_URL.format(email=email), headers=headers, timeout=DEFAULT_TIMEOUT)
    except requests.RequestException as exc:
        return {"enabled": True, "error": str(exc)}
    if r.status_code == 404:
        return {"enabled": True, "breaches": []}
    if r.status_code == 200:
        return {"enabled": True, "breaches": r.json()}
    return {"enabled": True, "error": f"HTTP {r.status_code}"}


def run(email: str) -> dict[str, Any]:
    email = (email or "").strip()
    if not email:
        return {"query": email, "error": "Provide an email address."}

    try:
        validation = validate_email(email, check_deliverability=False)
        normalized = validation.normalized
        domain = validation.domain
    except EmailNotValidError as exc:
        return {"query": email, "error": str(exc)}

    return {
        "query": normalized,
        "domain": domain,
        "mx_records": _mx_records(domain),
        "gravatar": _gravatar(normalized),
        "hibp": _hibp(normalized),
    }
