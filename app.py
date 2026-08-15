"""
Regional Voice Scam Shield
---------------------------
Flask backend for the hackathon prototype.

Flow:
  1. User records or types a call transcript (recording happens in the
     browser using the Web Speech API — see static/app.js).
  2. The transcript is sent to /scan.
  3. scan_transcript() checks it against scam-signal phrases stored in
     SQLite (see database.py) and returns a risk score.
  4. Every scan is logged to the detection_logs table so the team can
     show a history of past scans during the demo.
"""

from flask import Flask, render_template, request, jsonify
from database import init_db, get_db, seed_phrases_if_empty

app = Flask(__name__)

# Risk tiers, matched to the project's original slide deck.
def score_to_tier(n_categories_matched):
    if n_categories_matched == 0:
        return 5, "No risk detected"
    if n_categories_matched == 1:
        return 30, "Low risk"
    if n_categories_matched <= 3:
        return 70, "Medium risk"
    return 95, "High risk"


def scan_transcript(transcript: str):
    """Check a transcript against every scam-signal phrase in the DB.
    Returns the matched categories and the resulting risk tier."""
    text = transcript.lower()
    db = get_db()
    rows = db.execute(
        "SELECT category, phrase FROM scam_phrases"
    ).fetchall()

    matched = {}  # category -> first matching phrase
    for row in rows:
        category, phrase = row["category"], row["phrase"]
        if category in matched:
            continue
        if phrase.lower() in text:
            matched[category] = phrase

    pct, label = score_to_tier(len(matched))
    return {
        "matched": [{"category": c, "phrase": p} for c, p in matched.items()],
        "risk_pct": pct,
        "risk_label": label,
    }


@app.route("/")
def index():
    db = get_db()
    history = db.execute(
        "SELECT transcript, risk_pct, risk_label, created_at "
        "FROM detection_logs ORDER BY id DESC LIMIT 8"
    ).fetchall()
    return render_template("index.html", history=history)


@app.route("/scan", methods=["POST"])
def scan():
    data = request.get_json(force=True)
    transcript = (data.get("transcript") or "").strip()
    if not transcript:
        return jsonify({"error": "Transcript is empty."}), 400

    result = scan_transcript(transcript)

    db = get_db()
    db.execute(
        "INSERT INTO detection_logs (transcript, risk_pct, risk_label) "
        "VALUES (?, ?, ?)",
        (transcript, result["risk_pct"], result["risk_label"]),
    )
    db.commit()

    return jsonify(result)


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_phrases_if_empty()
    app.run(debug=True, port=5000)
