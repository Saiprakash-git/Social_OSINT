import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS

from services.aggregator import aggregate_results

app = Flask(__name__)
CORS(app)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/search")
def search():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()

    if not username:
        return jsonify({"error": "username is required"}), 400

    # run all providers concurrently
    results = asyncio.run(aggregate_results(username))

    return jsonify({
        "username": username,
        "count": len([r for r in results if r.get("exists")]),
        "results": results
    })

if __name__ == "__main__":
    # Dev server
    app.run(host="0.0.0.0", port=5000, debug=True)
