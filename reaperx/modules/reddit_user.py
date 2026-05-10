"""Reddit user recon via the public www.reddit.com JSON endpoints."""

from __future__ import annotations

from typing import Any

import requests

DEFAULT_TIMEOUT = 8
USER_AGENT = "ReaperX-OSINT/0.2 (+https://github.com/alertbros0/ReaperX)"


def _headers() -> dict[str, str]:
    return {"User-Agent": USER_AGENT, "Accept": "application/json"}


def _about(username: str) -> dict[str, Any]:
    r = requests.get(
        f"https://www.reddit.com/user/{username}/about.json",
        headers=_headers(),
        timeout=DEFAULT_TIMEOUT,
    )
    if r.status_code == 404:
        return {"_status": 404}
    r.raise_for_status()
    payload = r.json().get("data") or {}
    return {
        "_status": 200,
        "name": payload.get("name"),
        "id": payload.get("id"),
        "link_karma": payload.get("link_karma"),
        "comment_karma": payload.get("comment_karma"),
        "total_karma": payload.get("total_karma"),
        "is_gold": payload.get("is_gold"),
        "is_mod": payload.get("is_mod"),
        "is_employee": payload.get("is_employee"),
        "verified": payload.get("verified"),
        "has_verified_email": payload.get("has_verified_email"),
        "created_utc": payload.get("created_utc"),
        "icon_img": (payload.get("icon_img") or "").split("?")[0],
        "snoovatar_img": payload.get("snoovatar_img"),
        "subreddit": (payload.get("subreddit") or {}).get("display_name_prefixed"),
        "public_description": (payload.get("subreddit") or {}).get("public_description"),
    }


def _listing(username: str, kind: str, limit: int = 10) -> list[dict[str, Any]]:
    r = requests.get(
        f"https://www.reddit.com/user/{username}/{kind}.json",
        params={"limit": limit, "raw_json": 1},
        headers=_headers(),
        timeout=DEFAULT_TIMEOUT,
    )
    if not r.ok:
        return []
    children = (r.json().get("data") or {}).get("children") or []
    out: list[dict[str, Any]] = []
    for c in children:
        d = c.get("data") or {}
        if kind == "submitted":
            out.append(
                {
                    "title": d.get("title"),
                    "subreddit": d.get("subreddit_name_prefixed"),
                    "score": d.get("score"),
                    "num_comments": d.get("num_comments"),
                    "created_utc": d.get("created_utc"),
                    "permalink": f"https://www.reddit.com{d.get('permalink', '')}",
                    "url": d.get("url"),
                }
            )
        else:
            body = d.get("body") or ""
            out.append(
                {
                    "subreddit": d.get("subreddit_name_prefixed"),
                    "score": d.get("score"),
                    "created_utc": d.get("created_utc"),
                    "body_excerpt": body[:240] + ("…" if len(body) > 240 else ""),
                    "permalink": f"https://www.reddit.com{d.get('permalink', '')}",
                    "link_title": d.get("link_title"),
                }
            )
    return out


def run(username: str) -> dict[str, Any]:
    username = (username or "").strip().lstrip("@").lstrip("u/").lstrip("/")
    if not username:
        return {"error": "Username required."}
    try:
        about = _about(username)
    except requests.RequestException as exc:
        return {"query": username, "error": f"Reddit request failed: {exc}"}
    if about.get("_status") == 404:
        return {"query": username, "found": False, "error": "User not found."}
    about.pop("_status", None)
    posts = _listing(username, "submitted")
    comments = _listing(username, "comments")
    return {
        "query": username,
        "found": True,
        "profile_url": f"https://www.reddit.com/user/{username}",
        "about": about,
        "recent_posts": posts,
        "recent_comments": comments,
    }
