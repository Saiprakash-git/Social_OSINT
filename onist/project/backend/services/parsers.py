from bs4 import BeautifulSoup
from typing import Dict

# Parse OpenGraph/meta from an HTML response text

def parse_metadata(html: str) -> Dict[str, str]:
    soup = BeautifulSoup(html, "lxml")
    meta = {}
    for tag in soup.find_all("meta"):
        k = (tag.get("property") or tag.get("name") or "").strip().lower()
        v = (tag.get("content") or "").strip()
        if not k or not v:
            continue
        meta[k] = v
    # Common og fields we care about
    out = {
        "title": meta.get("og:title") or meta.get("twitter:title") or "",
        "description": meta.get("og:description") or meta.get("twitter:description") or "",
        "image": meta.get("og:image") or meta.get("twitter:image") or "",
    }
    return out