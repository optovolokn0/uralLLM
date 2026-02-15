import json
import faiss
from sqlalchemy import text
from db.session import SessionLocal
from embeddings.model import get_model

INDEX_PATH = "faiss_index/posts.index"
ID_MAP_PATH = "faiss_index/id_map.json"

def search_similar(text_query: str, top_k=5, min_score: float = 0.2):
    model = get_model()
    session = SessionLocal()

    index = faiss.read_index(INDEX_PATH)
    with open(ID_MAP_PATH, encoding="utf-8") as f:
        id_map = json.load(f)

    search_k = min(max(top_k * 3, top_k), len(id_map))

    query_vec = model.encode(
        [text_query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    scores, indices = index.search(query_vec, search_k)

    results = []
    seen_texts = set()

    for idx, score in zip(indices[0], scores[0]):
        if idx < 0 or idx >= len(id_map):
            continue

        score = float(score)
        if score < min_score:
            continue

        post_id = id_map[idx]
        row = session.execute(text("""
            SELECT clean_text
            FROM clean_posts
            WHERE id = :id
        """), {"id": post_id}).fetchone()

        if not row or not row.clean_text:
            continue

        normalized_text = row.clean_text.strip()
        if not normalized_text or normalized_text in seen_texts:
            continue

        seen_texts.add(normalized_text)
        results.append({
            "score": score,
            "text": normalized_text
        })

        if len(results) >= top_k:
            break

    session.close()
    return results
