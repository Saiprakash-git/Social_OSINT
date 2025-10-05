# x_client.py
import os, requests
from dotenv import load_dotenv
load_dotenv()

API_BASE = "https://api.x.com/2"  # change to 'https://api.twitter.com/2' if required by your environment
BEARER = os.environ.get("X_BEARER_TOKEN")

HEADERS = {"Authorization": f"Bearer {BEARER}"} if BEARER else {}

def get_x_user_by_username(username):
    """
    Returns X user object or {'error':...}
    """
    if not BEARER:
        return {"error":"No X_BEARER_TOKEN set in environment."}
    url = f"{API_BASE}/users/by/username/{username}"
    params = {"user.fields":"created_at,description,location,profile_image_url,public_metrics,url,verified"}
    r = requests.get(url, headers=HEADERS, params=params, timeout=10)
    if r.status_code == 200:
        return r.json()
    else:
        # return status and message for debugging
        return {"error": r.text, "status_code": r.status_code}

def get_x_user_tweets(user_id, max_results=50):
    if not BEARER:
        return {"error":"No X_BEARER_TOKEN set."}
    url = f"{API_BASE}/users/{user_id}/tweets"
    params = {"max_results": max_results, "tweet.fields":"created_at,public_metrics,entities,lang"}
    r = requests.get(url, headers=HEADERS, params=params, timeout=10)
    if r.status_code == 200:
        return r.json()
    else:
        return {"error": r.text, "status_code": r.status_code}
