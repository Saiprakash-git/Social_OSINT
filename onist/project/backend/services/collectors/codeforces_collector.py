import requests

def fetch_codeforces(username: str):
    url = f"https://codeforces.com/api/user.info?handles={username}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()["result"][0]
        return {
            "platform": "Codeforces",
            "username": data.get("handle"),
            "rating": data.get("rating"),
            "maxRating": data.get("maxRating"),
            "url": f"https://codeforces.com/profile/{username}"
        }
    return None
