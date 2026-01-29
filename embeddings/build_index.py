import json
import numpy as np
import faiss
from db.session import SessionLocal
from sqlalchemy import text
from embeddings.model import get_model

INDEX_PATH = "faiss_index/posts.index"
ID_MAP_PATH = "faiss_index/id_map.json"

def build_faiss_index():
    session = SessionLocal()
    model = get_model()

    rows = session.execute(text("""
        SELECT id, clean_text
        FROM clean_posts
    """)).fetchall()

    if not rows:
        print("No clean posts found")
        return

    texts = [r.clean_text for r in rows]
    ids = [r.id for r in rows]

    print(f"Embedding {len(texts)} posts...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity

    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)

    with open(ID_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(ids, f)

    session.close()
    print("FAISS index built successfully")
