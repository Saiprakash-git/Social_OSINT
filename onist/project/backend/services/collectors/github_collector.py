import requests

def fetch_github(username: str):
    url = f"https://api.github.com/users/{username}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return {
            "platform": "GitHub",
            "username": data.get("login"),
            "name": data.get("name"),
            "bio": data.get("bio"),
            "url": data.get("html_url"),
            "followers": data.get("followers"),
            "email": data.get("email")
        }
    return None
