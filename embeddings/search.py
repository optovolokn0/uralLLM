import json
import faiss
import numpy as np
from sqlalchemy import text
from db.session import SessionLocal
from embeddings.model import get_model

INDEX_PATH = "faiss_index/posts.index"
ID_MAP_PATH = "faiss_index/id_map.json"

def search_similar(text_query: str, top_k=5):
    model = get_model()
    session = SessionLocal()

    index = faiss.read_index(INDEX_PATH)
    with open(ID_MAP_PATH, encoding="utf-8") as f:
        id_map = json.load(f)

    query_vec = model.encode(
        [text_query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    scores, indices = index.search(query_vec, top_k)

    results = []
    for idx, score in zip(indices[0], scores[0]):
        post_id = id_map[idx]
        row = session.execute(text("""
            SELECT clean_text
            FROM clean_posts
            WHERE id = :id
        """), {"id": post_id}).fetchone()

        results.append({
            "score": float(score),
            "text": row.clean_text
        })

    session.close()
    return results
