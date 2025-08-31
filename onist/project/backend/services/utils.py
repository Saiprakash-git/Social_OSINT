import httpx
import datetime as dt
from typing import Optional, Tuple

DEFAULT_TIMEOUT = httpx.Timeout(12.0, connect=5.0)

async def get_json(url: str, headers: Optional[dict] = None) -> Tuple[Optional[dict], Optional[int]]:
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, headers=headers) as client:
        r = await client.get(url)
        try:
            return r.json(), r.status_code
        except Exception:
            return None, r.status_code

def now_iso() -> str:
    return dt.datetime.utcnow().isoformat() + "Z"