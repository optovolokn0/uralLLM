import requests
import time
from datetime import datetime
from db.session import SessionLocal
from db.models import VKGroup, RawPost
from config import VK_TOKEN, VK_API_VERSION

API_URL = "https://api.vk.com/method/wall.get"

def fetch_posts(vk_group_id: str, max_posts=1000):
    session = SessionLocal()

    group = session.query(VKGroup).filter_by(vk_group_id=vk_group_id).first()
    if not group:
        group = VKGroup(vk_group_id=vk_group_id, name=vk_group_id)
        session.add(group)
        session.commit()

    offset = 0
    collected = 0

    while collected < max_posts:
        params = {
            "access_token": VK_TOKEN,
            "v": VK_API_VERSION,
            "owner_id": f"-{vk_group_id}",
            "count": 100,
            "offset": offset
        }

        resp = requests.get(API_URL, params=params).json()
        if "error" in resp:
            print("VK API error:", resp["error"])
            break
        items = resp.get("response", {}).get("items", [])

        if not items:
            break

        for item in items:
            post_id = f"{vk_group_id}_{item['id']}"
            exists = session.query(RawPost).filter_by(vk_post_id=post_id).first()
            if exists:
                continue

            post = RawPost(
                vk_post_id=post_id,
                group_id=group.id,
                raw_text=item.get("text", ""),
                post_date=datetime.fromtimestamp(item["date"]),
                likes=item["likes"]["count"]
            )
            session.add(post)
            collected += 1

        session.commit()
        offset += 100
        time.sleep(0.34)

    session.close()
    print(f"Collected {collected} posts from {vk_group_id}")


# Запуск - fetch_posts("id группы", max_posts=)