import requests

def fetch_reddit(username: str):
    url = f"https://www.reddit.com/user/{username}/about.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()["data"]
        return {
            "platform": "Reddit",
            "username": data.get("name"),
            "karma": data.get("total_karma"),
            "url": f"https://reddit.com/user/{username}"
        }
    return None
