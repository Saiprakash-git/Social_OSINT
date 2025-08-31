import requests

def fetch_stackoverflow(username: str):
    # StackOverflow requires numeric user_id, not username
    # Placeholder logic (needs API key for production)
    return {
        "platform": "StackOverflow",
        "username": username,
        "url": f"https://stackoverflow.com/users/{username}"
    }
