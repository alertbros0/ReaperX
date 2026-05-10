"""Domain WHOIS + DNS records lookup."""

from __future__ import annotations

from typing import Any

import dns.exception
import dns.resolver
import whois

DEFAULT_RECORD_TYPES = ("A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA")


def _whois_lookup(domain: str) -> dict[str, Any]:
    try:
        data = whois.whois(domain)
    except Exception as exc:  # python-whois raises a variety of types
        return {"error": f"WHOIS query failed: {exc}"}

    def _stringify(v: Any) -> Any:
        if isinstance(v, list):
            return [_stringify(x) for x in v]
        if hasattr(v, "isoformat"):
            return v.isoformat()
        return v

    out = {}
    for key in (
        "domain_name",
        "registrar",
        "creation_date",
        "expiration_date",
        "updated_date",
        "name_servers",
        "status",
        "emails",
        "org",
        "country",
    ):
        if key in data:
            out[key] = _stringify(data.get(key))
    return out


def _dns_lookup(domain: str, record_types: tuple[str, ...] = DEFAULT_RECORD_TYPES) -> dict[str, Any]:
    resolver = dns.resolver.Resolver()
    resolver.lifetime = 5.0
    out: dict[str, list[str]] = {}
    for rtype in record_types:
        try:
            answers = resolver.resolve(domain, rtype)
            out[rtype] = sorted({rdata.to_text() for rdata in answers})
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
            out[rtype] = []
        except Exception as exc:
            out[rtype] = [f"<error: {exc}>"]
    return out


def run(domain: str) -> dict[str, Any]:
    domain = (domain or "").strip().lower().lstrip("*.")
    if not domain or "." not in domain:
        return {"query": domain, "error": "Provide a fully-qualified domain name."}
    return {
        "query": domain,
        "whois": _whois_lookup(domain),
        "dns": _dns_lookup(domain),
    }
