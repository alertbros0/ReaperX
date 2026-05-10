"""ReaperX OSINT modules.

Each module exposes a ``run(...)`` function that takes user-supplied input and
returns a JSON-serialisable dict describing the findings. All modules operate
purely on **publicly available** information.
"""

from reaperx.modules import (
    dorks,
    email,
    exif,
    ip,
    phone,
    ssl_cert,
    subdomains,
    username,
    wayback,
    whois_domain,
)

__all__ = [
    "dorks",
    "email",
    "exif",
    "ip",
    "phone",
    "ssl_cert",
    "subdomains",
    "username",
    "wayback",
    "whois_domain",
]
