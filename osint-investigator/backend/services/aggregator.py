import aiohttp
import asyncio
from typing import List, Dict, Any
# Import provider modules and headers from providers.py 

from .providers import (
    github,
    gitlab,
    reddit,
    devto,
    codeforces,
    hackernews,
    stackoverflow,
    HEADERS_JSON,
)

PROVIDERS = [
    github,
    gitlab,
    reddit,
    devto,
    codeforces,
    hackernews,
    stackoverflow,
]

async def aggregate_results(username: str) -> List[Dict[str, Any]]:
    async with aiohttp.ClientSession(headers=HEADERS_JSON) as session:
        tasks = [prov(session, username) for prov in PROVIDERS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    clean = []
    for r in results:
        if isinstance(r, Exception):
            # Normalize any unexpected provider errors
            clean.append({"platform": "unknown", "exists": False, "error": str(r)})
        else:
            clean.append(r)
    return clean
