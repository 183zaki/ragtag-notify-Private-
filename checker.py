import json
import os
import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]
SEARCH_URL = "https://www.ragtag.jp/search?q=satisfy"
SEEN_PATH = "seen.json"


def load_seen() -> set[str]:
    try:
        with open(SEEN_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("ids", []))
    except FileNotFoundError:
        return set()


def save_seen(ids: set[str]) -> None:
    data = {
        "ids": sorted(ids),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source": SEARCH_URL,
    }
    with open(SEEN_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_item_id(href: str) -> str | None:
    # 例: /item/1234567890123/
    m = re.search(r"/item/(\d+)", href)
    return m.group(1) if m else None


def main():
    print("Start Ragtag checker")

    r = requests.get(SEARCH_URL, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    print("Status:", r.status_code)

    soup = BeautifulSoup(r.text, "html.parser")

    # 検索結果から item リンクを拾う
    item_links = []
    for a in soup.select('a[href*="/item/"]'):
        href = a.get("href")
        if not href:
            continue
        item_id = extract_item_id(href)
        if not item_id:
            continue
        url = "https://www.ragtag.jp" + href
        title = a.get_text(" ", strip=True) or "Satisfy item"
        item_links.append((item_id, title, url))

    # 重複除去（同一 item_id）
    unique = {}
    for item_id, title, url in item_links:
        unique[item_id] = (title, url)

    print("Unique item links:", len(unique))

    seen = load_seen()
    current_ids = set(unique.keys())

    new_ids = sorted(current_ids - seen)
    print("New items:", len(new_ids))

    # seen を更新（通知の有無に関係なく最新を保存）
    save_seen(current_ids)

    # 新規だけ通知（最大5件まで）
    for item_id in new_ids[:5]:
        title, url = unique[item_id]
        msg = f"🆕 Satisfy 新着\n{title}\n{url}"
        resp = requests.post(WEBHOOK, json={"content": msg}, timeout=20)
        print("Sent", item_id, "status", resp.status_code)


if __name__ == "__main__":
    main()
