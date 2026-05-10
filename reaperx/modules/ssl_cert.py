"""Inspect the X.509 certificate served by a host on port 443 (or custom)."""

from __future__ import annotations

import socket
import ssl
from datetime import datetime, timezone
from typing import Any

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ExtensionOID, NameOID

DEFAULT_TIMEOUT = 8


def _name_to_dict(name: x509.Name) -> dict[str, str]:
    out: dict[str, str] = {}
    mapping = {
        NameOID.COMMON_NAME: "CN",
        NameOID.ORGANIZATION_NAME: "O",
        NameOID.ORGANIZATIONAL_UNIT_NAME: "OU",
        NameOID.COUNTRY_NAME: "C",
        NameOID.STATE_OR_PROVINCE_NAME: "ST",
        NameOID.LOCALITY_NAME: "L",
        NameOID.EMAIL_ADDRESS: "emailAddress",
    }
    for attr in name:
        key = mapping.get(attr.oid, attr.oid.dotted_string)
        out[key] = attr.value
    return out


def _san(cert: x509.Certificate) -> list[str]:
    try:
        ext = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
    except x509.ExtensionNotFound:
        return []
    return [str(v) for v in ext.value.get_values_for_type(x509.DNSName)]


def run(host: str, port: int = 443) -> dict[str, Any]:
    host = (host or "").strip().lower()
    if not host:
        return {"query": host, "error": "Provide a host."}

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with socket.create_connection((host, port), timeout=DEFAULT_TIMEOUT) as sock, \
                ctx.wrap_socket(sock, server_hostname=host) as ssock:
            der = ssock.getpeercert(binary_form=True)
    except (OSError, ssl.SSLError) as exc:
        return {"query": host, "error": f"TLS connection failed: {exc}"}

    cert = x509.load_der_x509_certificate(der, default_backend())

    not_before = cert.not_valid_before_utc if hasattr(cert, "not_valid_before_utc") else cert.not_valid_before.replace(tzinfo=timezone.utc)
    not_after = cert.not_valid_after_utc if hasattr(cert, "not_valid_after_utc") else cert.not_valid_after.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    return {
        "query": f"{host}:{port}",
        "subject": _name_to_dict(cert.subject),
        "issuer": _name_to_dict(cert.issuer),
        "serial_number": format(cert.serial_number, "x"),
        "version": cert.version.name,
        "not_before": not_before.isoformat(),
        "not_after": not_after.isoformat(),
        "expires_in_days": (not_after - now).days,
        "is_expired": now > not_after,
        "signature_algorithm": cert.signature_hash_algorithm.name if cert.signature_hash_algorithm else None,
        "subject_alt_names": _san(cert),
    }
