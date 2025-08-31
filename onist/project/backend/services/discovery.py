# services/discovery.py

from services.collectors.github import GitHubCollector
from services.collectors.twitter import TwitterCollector
from services.collectors.instagram import InstagramCollector

from services.collectors.github_collector import fetch_github_profile
class DiscoveryService:
    def __init__(self):
        self.collectors = {
            "github": GitHubCollector(),
            "twitter": TwitterCollector(),
            "instagram": InstagramCollector(),
        }

    def find_user(self, username: str):
        """
        Runs discovery across all collectors and aggregates results.
        """
        results = {}
        for name, collector in self.collectors.items():
            try:
                data = collector.search(username)
                if data:
                    results[name] = data
            except Exception as e:
                results[name] = {"error": str(e)}
        return results
