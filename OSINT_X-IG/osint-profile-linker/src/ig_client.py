import instaloader
import time
from instaloader.exceptions import ConnectionException, LoginRequiredException

# CONFIG — Replace with your own Instagram username
IG_USERNAME = "insta_user_osint"  # same as in login_session.py

def get_ig_profile(username, max_posts=5):
    L = instaloader.Instaloader()

    # --- Load the saved session ---
    try:
        L.load_session_from_file(IG_USERNAME)
        print(f"✅ Logged in successfully as {IG_USERNAME}")
    except Exception as e:
        print("⚠️ Could not load session file. Attempting anonymous mode:", e)

    # --- Fetch the profile with error handling ---
    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except (ConnectionException, LoginRequiredException) as e:
        print(f"⚠️ Instagram blocked or unauthorized: {e}")
        print("🕒 Waiting 60 seconds before retry...")
        time.sleep(60)
        # Retry once after waiting
        profile = instaloader.Profile.from_username(L.context, username)

    # --- Extract profile details ---
    data = {
        "username": profile.username,
        "full_name": profile.full_name,
        "followers": profile.followers,
        "following": profile.followees,
        "bio": profile.biography,
        "profile_pic_url": profile.profile_pic_url,
        "posts": []
    }

    # --- Fetch a limited number of posts ---
    try:
        count = 0
        for post in profile.get_posts():
            if count >= max_posts:
                break
            data["posts"].append({
                "caption": post.caption,
                "likes": post.likes,
                "comments": post.comments,
                "date": post.date_utc.isoformat(),
                "url": post.url
            })
            count += 1
    except ConnectionException as e:
        print("⚠️ Failed while fetching posts, partial data returned:", e)

    return data
