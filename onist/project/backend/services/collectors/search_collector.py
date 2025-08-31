import os
import requests

BING_KEY = os.getenv("BING_API_KEY")
BING_URL = "https://api.bing.microsoft.com/v7.0/search"

def search_socials(username: str):
    query = f"{username} site:instagram.com OR site:twitter.com OR site:linkedin.com OR site:facebook.com"
    headers = {"Ocp-Apim-Subscription-Key": BING_KEY}
    r = requests.get(BING_URL, headers=headers, params={"q": query})
    results = []
    if r.status_code == 200:
        for web_page in r.json().get("webPages", {}).get("value", []):
            results.append({
                "platform": "Social",
                "title": web_page["name"],
                "snippet": web_page["snippet"],
                "url": web_page["url"]
            })
    return results
