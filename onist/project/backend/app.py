from flask import Flask, jsonify 

from services.collectors.github_collector import fetch_github_profile
from services.collectors.reddit_collector import fetch_reddit_profile
from services.collectors.devto_collector import fetch_devto_profile
from services.collectors.search_collector import search_social_links
import os


app = Flask(__name__)

# Health check
@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "Social OSINT API running!"})


# Main search route
@app.route("/search/<username>", methods=["GET"])
def search_username(username):
    results = {}

    try:
        results["github"] = fetch_github_profile(username)
    except Exception as e:
        results["github"] = {"error": str(e)}

    try:
        results["reddit"] = fetch_reddit_profile(username)
    except Exception as e:
        results["reddit"] = {"error": str(e)}

    try:
        results["devto"] = fetch_devto_profile(username)
    except Exception as e:
        results["devto"] = {"error": str(e)}

    try:
        results["social_links"] = search_social_links(username)
    except Exception as e:
        results["social_links"] = {"error": str(e)}

    return jsonify({"username": username, "results": results})


if __name__ == "__main__":
    # Run on http://127.0.0.1:5000
    app.run(debug=True)
