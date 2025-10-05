# matcher.py
from config import WEIGHTS
from features import username_similarity, text_embedding_similarity, image_phash_similarity
import numpy as np

def compute_match_score(ig_profile, x_profile):
    """
    ig_profile: dict with keys 'username','full_name','bio','profile_pic_url','posts'
    x_profile: dict as returned from X API (user object inside 'data')
    Returns: dict with per-feature scores, final score, explanation
    """
    igu = ig_profile.get("username","")
    igname = ig_profile.get("full_name","") or ""
    igbio = ig_profile.get("bio","") or ""
    igpic = ig_profile.get("profile_pic_url","")
    # x_profile expected to be {'data': {...}}
    xdata = x_profile.get("data") if isinstance(x_profile, dict) else x_profile
    if not xdata:
        return {"final_score":0.0, "explanation":"No X profile data"}

    xu = xdata.get("username","")
    xname = xdata.get("name","") or ""
    xbio = xdata.get("description","") or ""
    xpic = xdata.get("profile_image_url","") or ""

    scores = {}
    scores['username'] = username_similarity(igu, xu)
    scores['display_name'] = text_embedding_similarity(igname, xname)
    scores['bio'] = text_embedding_similarity(igbio, xbio)
    scores['image'] = image_phash_similarity(igpic, xpic) if igpic and xpic else 0.0

    # link similarity: naive check
    iglink = ig_profile.get("external_url") or ""
    xlink = xdata.get("url") or ""
    scores['link'] = 1.0 if iglink and xlink and (iglink.split("//")[-1].split("/")[0] == xlink.split("//")[-1].split("/")[0]) else 0.0

    # activity similarity: compare aggregated IG captions vs X bio+maybe tweets text (simple)
    ig_text = " ".join([p.get("caption","") for p in ig_profile.get("posts",[])])
    x_text = (xbio + " " + " ").strip()
    scores['activity'] = text_embedding_similarity(ig_text, x_text)

    # weighted sum
    final = 0.0
    for k,w in WEIGHTS.items():
        final += scores.get(k,0.0) * w

    return {"final_score": float(final), "scores": scores, "x_username": xu, "x_name": xname, "x_bio": xbio}
