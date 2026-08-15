# Regional Voice Scam Shield

A hackathon prototype that reads a call transcript (typed or voice-recorded
in the browser) and scores it for scam-call risk using regional-language
pattern matching — English, Tamil, and Hindi phrases for six common scam
signals (urgency, OTP/money requests, impersonation, KYC threats, family
emergencies, job-offer bait).

## How it works

- `database.py` creates two SQLite tables: `scam_phrases` (the phrase
  dictionary — edit this to add more phrases or languages) and
  `detection_logs` (every scan you run, so you can show a history live).
- `app.py` is the Flask server. `/` shows the page and recent scan
  history; `/scan` receives a transcript, checks it against
  `scam_phrases`, and returns a risk score.
- `static/app.js` handles the microphone recording (using the browser's
  built-in Web Speech API — no API key, no cost) and sends the resulting
  transcript to `/scan`.
- `templates/index.html` + `static/style.css` are the page itself.

Risk scoring: 0 categories matched → 5% (no risk), 1 → 30% (low),
2–3 → 70% (medium), 4+ → 95% (high).

## Run it locally

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in Chrome (voice recording needs Chrome
or Edge — it uses `webkitSpeechRecognition`, not supported in Firefox/Safari).
Typing a transcript and pressing "Scan transcript" always works regardless
of browser.

The first run creates `scam_shield.db` automatically and seeds it with the
starter phrase dictionary.

## Push it to GitHub — step by step

1. **Create the repo on GitHub.** Go to github.com → New repository →
   name it (e.g. `voice-scam-shield`) → do **not** initialize with a
   README (you already have one) → Create repository.

2. **Initialize git locally**, from inside the `scam-shield` folder:
   ```bash
   git init
   git add .
   git commit -m "Initial commit — scam shield prototype"
   ```

3. **Connect it to the GitHub repo** (copy the URL GitHub shows you
   after step 1 — it looks like `https://github.com/<you>/voice-scam-shield.git`):
   ```bash
   git branch -M main
   git remote add origin https://github.com/<you>/voice-scam-shield.git
   git push -u origin main
   ```

4. **From then on**, after any change:
   ```bash
   git add .
   git commit -m "describe what changed"
   git push
   ```

5. **If your team is pushing together:** each teammate should clone the
   repo (`git clone https://github.com/<you>/voice-scam-shield.git`)
   rather than re-zipping and re-uploading — that's what keeps commit
   history (and each person's contribution) visible, which judges often
   check.

## Extending it

- Add more phrases per language directly in `database.py` →
  `PHRASE_SEED`, or write directly into the `scam_phrases` table.
- To record in Tamil or Hindi instead of English, change
  `recognizer.lang` in `static/app.js` to `'ta-IN'` or `'hi-IN'`.
- Next milestones from the original design: voice-authenticity/deepfake
  detection, and moving from "record then scan" to live in-call scanning.
