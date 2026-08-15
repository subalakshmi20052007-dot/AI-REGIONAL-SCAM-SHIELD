"""
Database layer — plain sqlite3, no ORM, so it's easy to open the .db
file in any SQLite browser and show judges the raw tables.
"""

import sqlite3
from flask import g

DB_PATH = "scam_shield.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS scam_phrases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            phrase TEXT NOT NULL,
            language TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS detection_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcript TEXT NOT NULL,
            risk_pct INTEGER NOT NULL,
            risk_label TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    db.commit()


# category -> (language, [phrases])
# Edit or extend this dictionary freely — it's the whole detection engine.
PHRASE_SEED = {
    "urgency": [
        ("en", ["urgent", "immediately", "right now", "act now",
                "before it's too late", "last chance", "hurry"]),
        ("ta", ["இப்போதே", "உடனடியாக", "இப்பவே", "அவசரம்"]),
        ("hi", ["अभी", "तुरंत", "जल्दी", "जल्द से जल्द"]),
    ],
    "money_otp": [
        ("en", ["otp", "one time password", "upi pin", "send money",
                "transfer money", "bank account number", "cvv", "card number"]),
        ("ta", ["பணத்தை அனுப்பு", "otp சொல்லுங்க"]),
        ("hi", ["रुपये भेजो", "ओटीपी बताओ", "पैसे भेजो"]),
    ],
    "impersonation": [
        ("en", ["bank manager", "police department", "government office",
                "income tax department", "calling from rbi", "cyber cell",
                "customs department", "this is your son"]),
        ("ta", ["பேங்க் மேலாளர்", "போலீஸ் துறை"]),
        ("hi", ["सरकारी दफ्तर", "पुलिस विभाग"]),
    ],
    "kyc": [
        ("en", ["kyc verification", "update your kyc", "kyc update",
                "account will be blocked", "account has been suspended", "kyc"]),
        ("ta", ["கேஒய்சி"]),
        ("hi", ["केवाईसी"]),
    ],
    "family_emergency": [
        ("en", ["accident", "hospital", "in jail", "arrested",
                "emergency", "need money now"]),
        ("ta", ["விபத்து", "மருத்துவமனை"]),
        ("hi", ["जेल में", "दुर्घटना", "अस्पताल में"]),
    ],
    "job_offer": [
        ("en", ["work from home", "guaranteed income", "registration fee",
                "part time job", "earn from home"]),
        ("ta", ["வேலை வாய்ப்பு"]),
        ("hi", ["वर्क फ्रॉम होम", "गारंटीड इनकम", "रजिस्ट्रेशन"]),
    ],
}


def seed_phrases_if_empty():
    db = get_db()
    count = db.execute("SELECT COUNT(*) AS c FROM scam_phrases").fetchone()["c"]
    if count > 0:
        return
    rows = []
    for category, lang_groups in PHRASE_SEED.items():
        for language, phrases in lang_groups:
            for phrase in phrases:
                rows.append((category, phrase, language))
    db.executemany(
        "INSERT INTO scam_phrases (category, phrase, language) VALUES (?, ?, ?)",
        rows,
    )
    db.commit()
