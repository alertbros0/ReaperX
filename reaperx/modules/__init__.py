"""ReaperX OSINT modules.

Each module exposes a ``run(...)`` function that takes user-supplied input and
returns a JSON-serialisable dict describing the findings. All modules operate
purely on **publicly available** information.
"""

from reaperx.modules import (
    doh,
    dorks,
    email,
    exif,
    github_user,
    ip,
    mac_vendor,
    phone,
    reddit_user,
    reverse_image,
    ssl_cert,
    subdomains,
    threat_intel,
    username,
    wayback,
    whois_domain,
)

__all__ = [
    "doh",
    "dorks",
    "email",
    "exif",
    "github_user",
    "ip",
    "mac_vendor",
    "phone",
    "reddit_user",
    "reverse_image",
    "ssl_cert",
    "subdomains",
    "threat_intel",
    "username",
    "wayback",
    "whois_domain",
]
