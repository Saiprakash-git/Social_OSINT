# config.py
WEIGHTS = {
    "username": 0.25,
    "display_name": 0.20,
    "bio": 0.20,
    "image": 0.15,
    "link": 0.10,
    "activity": 0.10
}

API_BASE = "https://api.x.com/2"  # replace with correct X endpoint if needed
MAX_PERMUTATIONS = 50
CACHE_DIR = "../data/cached_samples"
