# app.py
import streamlit as st
from ig_client import get_ig_profile
from x_client import get_x_user_by_username, get_x_user_tweets
from matcher import compute_match_score
from utils import cache_save
from config import MAX_PERMUTATIONS
from features import username_similarity
import itertools
import time

# --- Streamlit page config ---
st.set_page_config(layout="wide", page_title="OSINT Profile Linker")

st.title("OSINT Profile Linker — IG → X (Twitter) Match & Analysis")
st.markdown("Enter an Instagram username (public) to find matching X accounts and generate a profile analysis.")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("Inputs")
    ig_username = st.text_input("Instagram username", placeholder="e.g., example_user")
    full_name_hint = st.text_input("Full name (optional)")
    location_hint = st.text_input("Location (optional)")
    posts_to_fetch = st.slider("Number of IG posts to fetch", 3, 24, 12)
    max_perms = st.number_input("Max username permutations to try (X)", min_value=5, max_value=200, value=50, step=5)

# --- Validate IG username input ---
if not ig_username:
    st.info("Enter an Instagram username on the left to begin.")
    st.stop()

# --- Main Analysis ---
if st.button("Analyze"):
    with st.spinner("Fetching Instagram profile..."):
        ig_profile = get_ig_profile(ig_username, max_posts=posts_to_fetch)
        if ig_profile.get("error"):
            st.error(f"IG fetch error: {ig_profile.get('error')}")
            st.stop()
    st.success("Instagram profile fetched.")

    # --- Visualize IG profile ---
    col1, col2 = st.columns([1,2])
    with col1:
        profile_pic = ig_profile.get("profile_pic_url") or "https://via.placeholder.com/150"
        st.image(profile_pic, width=180)
        st.markdown(f"**@{ig_profile.get('username','')}**")
        st.markdown(f"**Full name:** {ig_profile.get('full_name','')}")
        st.markdown(f"**Bio:** {ig_profile.get('bio','')}")
        st.markdown(f"**Followers:** {ig_profile.get('followers',0)} • **Following:** {ig_profile.get('followees',0)}")
    with col2:
        st.subheader("Recent posts (captions)")
        if ig_profile.get("posts"):
            for p in ig_profile.get("posts", []):
                caption = p.get("caption") or "(No caption)"
                st.write(f"- {p.get('date','')} — {caption[:300]}")
        else:
            st.write("No recent posts available.")

    # --- Generate username permutations (basic) ---
    base = ig_profile.get("username","")
    candidates = set()
    candidates.add(base)
    candidates.add(base.replace("_", ""))
    if full_name_hint:
        tokens = full_name_hint.split()
        for t in tokens:
            candidates.add(t.lower())
            candidates.add((t + base).lower())
    candidates.update({base + str(i) for i in range(1,6)})
    candidates.update({base + "." + str(i) for i in range(1,4)})
    candidates_list = list(candidates)[:max_perms]

    st.write("Trying candidate X usernames (limited by rate limits):")
    results = []
    for c in candidates_list:
        time.sleep(0.2)  # small delay to be polite
        xres = get_x_user_by_username(c)
        if xres.get("error"):
            continue
        match = compute_match_score(ig_profile, xres)
        match['candidate'] = c
        match['x_raw'] = xres
        results.append(match)

    # --- Sort by final score ---
    results_sorted = sorted(results, key=lambda r: r['final_score'], reverse=True)

    # --- Display results ---
    if not results_sorted:
        st.warning("No X candidates found from permutations. You can try 'Provide X username' option or increase permutations.")
    else:
        st.subheader("Top Matches")
        for r in results_sorted[:5]:
            sc = r['final_score']
            st.markdown(f"**@{r['candidate']}** — Score: **{sc:.2f}**")
            st.write("Per-feature scores:")
            for k,v in r['scores'].items():
                st.write(f"• {k}: {v:.2f}")
            xdata = r['x_raw'].get("data", {})
            x_pic = xdata.get("profile_image_url") or "https://via.placeholder.com/80"
            st.image(x_pic, width=80)
            st.write(f"Name: {xdata.get('name','')} — Bio: {xdata.get('description','')}")
            if sc >= 0.70:
                st.success("Likely match ✅")
            elif sc >= 0.45:
                st.info("Possible match (needs review) 🔎")
            else:
                st.write("Unlikely match")

    # --- Save cache for reproducibility ---
    cache_path = cache_save(f"ig_{ig_username}_results", {"ig": ig_profile, "results": results_sorted})
    st.markdown(f"Cached run saved to `{cache_path}` for reproducibility.")

    st.balloons()
