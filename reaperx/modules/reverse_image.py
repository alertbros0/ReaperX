"""Generate reverse-image-search links for an image URL.

This module is intentionally offline / deterministic: it constructs the
search URLs that each engine accepts and returns them for the user to open.
"""

from __future__ import annotations

import urllib.parse
from typing import Any

ENGINES = {
    "Google Lens": "https://lens.google.com/uploadbyurl?url={url}",
    "TinEye": "https://tineye.com/search?url={url}",
    "Yandex Images": "https://yandex.com/images/search?rpt=imageview&url={url}",
    "Bing Images": "https://www.bing.com/images/search?view=detailv2&iss=sbi&form=SBIVSP&q=imgurl:{url}",
    "SauceNAO": "https://saucenao.com/search.php?url={url}",
    "Karma Decay (Reddit)": "https://karmadecay.com/search?kdtoolver=b1&q={url}",
    "IQDB": "https://iqdb.org/?url={url}",
}


def run(url: str) -> dict[str, Any]:
    url = (url or "").strip()
    if not url:
        return {"error": "Image URL required."}
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return {"query": url, "error": "URL must be http(s) and include a host."}
    encoded = urllib.parse.quote(url, safe="")
    engines = [
        {"name": name, "url": template.format(url=encoded)}
        for name, template in ENGINES.items()
    ]
    return {
        "query": url,
        "image_host": parsed.netloc,
        "engines": engines,
    }
