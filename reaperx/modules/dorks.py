"""Generate ready-to-paste Google search queries (Google dorks).

Useful for OSINT pivots: finding public mentions, exposed documents, code
references, etc. Generated queries link to Google, Bing, and DuckDuckGo.
"""

from __future__ import annotations

import urllib.parse
from typing import Any

DORK_TEMPLATES = {
    "Mentions across the web": '"{q}"',
    "Site files (PDF/DOC/XLS)": '"{q}" filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx',
    "Pastebin / paste sites": 'site:pastebin.com OR site:ghostbin.com OR site:rentry.co "{q}"',
    "GitHub references": 'site:github.com "{q}"',
    "Twitter/X mentions": 'site:twitter.com OR site:x.com "{q}"',
    "Reddit mentions": 'site:reddit.com "{q}"',
    "LinkedIn profiles": 'site:linkedin.com/in "{q}"',
    "News articles": '"{q}" (site:nytimes.com OR site:bbc.com OR site:reuters.com OR site:apnews.com)',
    "Forum posts": 'inurl:forum OR inurl:thread "{q}"',
    "Public S3 buckets": 'site:s3.amazonaws.com "{q}"',
    "Open directories": '"{q}" intitle:"index of"',
    "Public Trello boards": 'site:trello.com "{q}"',
    "Public Google docs": 'site:docs.google.com "{q}"',
}

ENGINES = {
    "Google": "https://www.google.com/search?q=",
    "Bing": "https://www.bing.com/search?q=",
    "DuckDuckGo": "https://duckduckgo.com/?q=",
}


def run(query: str) -> dict[str, Any]:
    query = (query or "").strip()
    if not query:
        return {"query": query, "error": "Provide a target name, email, handle, etc."}

    rows: list[dict[str, Any]] = []
    for label, template in DORK_TEMPLATES.items():
        dork = template.format(q=query)
        engines = {name: f"{base}{urllib.parse.quote_plus(dork)}" for name, base in ENGINES.items()}
        rows.append({"label": label, "dork": dork, "engines": engines})

    return {"query": query, "dorks": rows}
