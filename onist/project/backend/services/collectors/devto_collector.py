import requests

def fetch_devto(username: str):
    url = f"https://dev.to/api/users/by_username?url={username}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return {
            "platform": "Dev.to",
            "username": data.get("username"),
            "name": data.get("name"),
            "url": f"https://dev.to/{username}"
        }
    return None
