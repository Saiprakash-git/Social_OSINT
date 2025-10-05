# features.py
from sentence_transformers import SentenceTransformer
import numpy as np
from PIL import Image
import imagehash
import requests
from io import BytesIO
import difflib
from sklearn.metrics.pairwise import cosine_similarity

MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(texts):
    # texts: list of strings
    return MODEL.encode(texts, convert_to_numpy=True)

def cosine_sim(a, b):
    if a is None or b is None: return 0.0
    a = a.reshape(1, -1) if a.ndim==1 else a
    b = b.reshape(1, -1) if b.ndim==1 else b
    return float(cosine_similarity(a, b)[0][0])

def username_similarity(u1, u2):
    if not u1 or not u2:
        return 0.0
    ratio = difflib.SequenceMatcher(None, u1.lower(), u2.lower()).ratio()
    return ratio  # 0..1

def image_phash_similarity(url1, url2):
    try:
        r1 = requests.get(url1, timeout=10)
        r2 = requests.get(url2, timeout=10)
        img1 = Image.open(BytesIO(r1.content)).convert("RGB")
        img2 = Image.open(BytesIO(r2.content)).convert("RGB")
        h1 = imagehash.phash(img1)
        h2 = imagehash.phash(img2)
        # hash distance -> normalize (0 distance => identical)
        max_hash = 64  # pHash gives 64-bit by default, but imagehash distance returns int <= 64
        dist = (h1 - h2)
        sim = 1 - (dist / max_hash)
        return max(0.0, min(1.0, sim))
    except Exception:
        return 0.0

def text_embedding_similarity(text1, text2):
    if not text1 or not text2:
        return 0.0
    e = embed_text([text1, text2])
    return float(cosine_similarity(e[0].reshape(1,-1), e[1].reshape(1,-1))[0][0])
