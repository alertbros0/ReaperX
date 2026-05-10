"""GitHub user recon via the public api.github.com endpoints."""

from __future__ import annotations

from typing import Any

import requests

DEFAULT_TIMEOUT = 8
USER_AGENT = "ReaperX-OSINT/0.2"


def _headers() -> dict[str, str]:
    return {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}


def _profile(username: str) -> dict[str, Any]:
    r = requests.get(
        f"https://api.github.com/users/{username}",
        headers=_headers(),
        timeout=DEFAULT_TIMEOUT,
    )
    if r.status_code == 404:
        return {"_status": 404}
    r.raise_for_status()
    data = r.json()
    return {
        "_status": 200,
        "login": data.get("login"),
        "id": data.get("id"),
        "name": data.get("name"),
        "bio": data.get("bio"),
        "company": data.get("company"),
        "location": data.get("location"),
        "blog": data.get("blog"),
        "twitter_username": data.get("twitter_username"),
        "email": data.get("email"),
        "public_repos": data.get("public_repos"),
        "public_gists": data.get("public_gists"),
        "followers": data.get("followers"),
        "following": data.get("following"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
        "html_url": data.get("html_url"),
        "avatar_url": data.get("avatar_url"),
        "hireable": data.get("hireable"),
    }


def _top_repos(username: str, limit: int = 10) -> list[dict[str, Any]]:
    r = requests.get(
        f"https://api.github.com/users/{username}/repos",
        params={"per_page": 100, "sort": "updated"},
        headers=_headers(),
        timeout=DEFAULT_TIMEOUT,
    )
    if not r.ok:
        return []
    repos = r.json() or []
    repos.sort(key=lambda x: x.get("stargazers_count", 0), reverse=True)
    out: list[dict[str, Any]] = []
    for repo in repos[:limit]:
        out.append(
            {
                "name": repo.get("name"),
                "html_url": repo.get("html_url"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "open_issues": repo.get("open_issues_count"),
                "is_fork": repo.get("fork"),
                "updated_at": repo.get("updated_at"),
            }
        )
    return out


def run(username: str) -> dict[str, Any]:
    username = (username or "").strip().lstrip("@")
    if not username:
        return {"error": "Username required."}
    try:
        profile = _profile(username)
    except requests.RequestException as exc:
        return {"query": username, "error": f"GitHub request failed: {exc}"}
    if profile.get("_status") == 404:
        return {"query": username, "found": False, "error": "User not found."}
    profile.pop("_status", None)
    repos = _top_repos(username)
    return {
        "query": username,
        "found": True,
        "profile": profile,
        "top_repos": repos,
        "repo_count_returned": len(repos),
    }
