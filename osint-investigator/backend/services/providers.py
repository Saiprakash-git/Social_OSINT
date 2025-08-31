import aiohttp
from typing import Dict, Any, Optional

JSON = Dict[str, Any]

DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=10)

HEADERS_JSON = {
    "Accept": "application/json",
    "User-Agent": "osint-investigator/1.0 (+https://example.local)"
}

async def fetch_json(session: aiohttp.ClientSession, url: str) -> Optional[JSON]:
    try:
        async with session.get(url, timeout=DEFAULT_TIMEOUT) as resp:
            if resp.status != 200:
                return None
            return await resp.json(content_type=None)
    except Exception:
        return None

def result_template(platform: str) -> JSON:
    return {
        "platform": platform,
        "exists": False,
        "username": None,
        "display_name": None,
        "url": None,
        "avatar_url": None,
        "bio": None,
    }

# ---------- Providers (public/official endpoints only) ----------

async def github(session: aiohttp.ClientSession, username: str) -> JSON:
    res = result_template("GitHub")
    url = f"https://api.github.com/users/{username}"
    data = await fetch_json(session, url)
    if not data or "login" not in data:
        return res
    res.update({
        "exists": True,
        "username": data.get("login"),
        "display_name": data.get("name") or data.get("login"),
        "url": f"https://github.com/{data.get('login')}",
        "avatar_url": data.get("avatar_url"),
        "bio": data.get("bio"),
        "extra": {
            "followers": data.get("followers"),
            "following": data.get("following"),
            "public_repos": data.get("public_repos"),
        }
    })
    return res

async def gitlab(session: aiohttp.ClientSession, username: str) -> JSON:
    res = result_template("GitLab")
    url = f"https://gitlab.com/api/v4/users?username={username}"
    data = await fetch_json(session, url)
    if not data or not isinstance(data, list) or len(data) == 0:
        return res
    u = data[0]
    res.update({
        "exists": True,
        "username": u.get("username"),
        "display_name": u.get("name") or u.get("username"),
        "url": u.get("web_url"),
        "avatar_url": u.get("avatar_url"),
        "bio": None
    })
    return res

async def reddit(session: aiohttp.ClientSession, username: str) -> JSON:
    # Reddit public user about endpoint (no auth for public profiles)
    res = result_template("Reddit")
    url = f"https://www.reddit.com/user/{username}/about.json"
    # Reddit is picky about UA header
    try:
        async with session.get(url, headers={
            **HEADERS_JSON,
            "User-Agent": "osint-investigator/1.0 (contact: demo@app)"
        }, timeout=DEFAULT_TIMEOUT) as resp:
            if resp.status != 200:
                return res
            data = await resp.json(content_type=None)
    except Exception:
        return res

    d = (data or {}).get("data") or {}
    if not d or d.get("is_suspended"):
        return res
    sub = d.get("subreddit") or {}
    res.update({
        "exists": True,
        "username": d.get("name"),
        "display_name": sub.get("title") or d.get("subreddit", {}).get("title"),
        "url": f"https://www.reddit.com/user/{d.get('name')}/",
        "avatar_url": d.get("icon_img") or sub.get("icon_img") or sub.get("community_icon"),
        "bio": sub.get("public_description")
    })
    return res

async def devto(session: aiohttp.ClientSession, username: str) -> JSON:
    res = result_template("Dev.to")
    url = f"https://dev.to/api/users/by_username?url={username}"
    data = await fetch_json(session, url)
    if not data or "username" not in data:
        return res
    res.update({
        "exists": True,
        "username": data.get("username"),
        "display_name": data.get("name") or data.get("username"),
        "url": f"https://dev.to/{data.get('username')}",
        "avatar_url": data.get("profile_image"),
        "bio": data.get("summary")
    })
    return res

async def codeforces(session: aiohttp.ClientSession, username: str) -> JSON:
    res = result_template("Codeforces")
    url = f"https://codeforces.com/api/user.info?handles={username}"
    data = await fetch_json(session, url)
    if not data or data.get("status") != "OK":
        return res
    items = data.get("result") or []
    if not items:
        return res
    u = items[0]
    res.update({
        "exists": True,
        "username": u.get("handle"),
        "display_name": u.get("firstName") and f"{u.get('firstName','')} {u.get('lastName','')}".strip() or u.get("handle"),
        "url": f"https://codeforces.com/profile/{u.get('handle')}",
        "avatar_url": u.get("avatar"),
        "bio": f"Rating: {u.get('rating')} ({u.get('rank')})" if u.get("rating") else None
    })
    return res

async def hackernews(session: aiohttp.ClientSession, username: str) -> JSON:
    res = result_template("HackerNews")
    url = f"https://hacker-news.firebaseio.com/v0/user/{username}.json"
    data = await fetch_json(session, url)
    if not data:
        return res
    res.update({
        "exists": True,
        "username": data.get("id"),
        "display_name": data.get("id"),
        "url": f"https://news.ycombinator.com/user?id={data.get('id')}",
        "avatar_url": None,  # HN doesn't provide avatars
        "bio": data.get("about")
    })
    return res

async def stackoverflow(session: aiohttp.ClientSession, username: str) -> JSON:
    """
    Stack Overflow users are ID-based; we approximate by searching display names.
    We'll return the best-matching top result (if any).
    """
    res = result_template("StackOverflow")
    # Note: rate-limited; for heavier use, register an API key.
    url = ("https://api.stackexchange.com/2.3/users"
           f"?order=desc&sort=reputation&inname={username}&site=stackoverflow")
    data = await fetch_json(session, url)
    if not data or not data.get("items"):
        return res
    item = data["items"][0]
    res.update({
        "exists": True,
        "username": item.get("display_name"),
        "display_name": item.get("display_name"),
        "url": item.get("link"),
        "avatar_url": item.get("profile_image"),
        "bio": None
    })
    return res
