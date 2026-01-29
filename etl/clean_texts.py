import re
from db.session import SessionLocal
from db.models import RawPost
from sqlalchemy import text

def clean_text(text: str) -> str:
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"#\w+", "", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()

def clean_posts(min_words=20):
    session = SessionLocal()

    session.execute(text("""
        CREATE TABLE IF NOT EXISTS clean_posts (
            id INTEGER PRIMARY KEY,
            raw_post_id INTEGER UNIQUE,
            clean_text TEXT,
            word_count INTEGER
        )
    """))

    raw_posts = session.query(RawPost).all()

    for post in raw_posts:
        cleaned = clean_text(post.raw_text)
        word_count = len(cleaned.split())

        if word_count < min_words:
            continue

        session.execute(text("""
            INSERT OR IGNORE INTO clean_posts (raw_post_id, clean_text, word_count)
            VALUES (:raw_id, :text, :count)
        """), {
            "raw_id": post.id,
            "text": cleaned,
            "count": word_count
        })

    session.commit()
    session.close()
    print("Cleaning finished")