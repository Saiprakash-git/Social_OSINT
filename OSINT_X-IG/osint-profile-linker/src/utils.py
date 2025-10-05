# utils.py
import os, json, hashlib
from pathlib import Path

def ensure_cache_dir():
    Path("data/cached_samples").mkdir(parents=True, exist_ok=True)

def cache_save(name, data):
    ensure_cache_dir()
    h = hashlib.sha1(name.encode()).hexdigest()[:10]
    path = f"data/cached_samples/{name}_{h}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path

def cache_load(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
