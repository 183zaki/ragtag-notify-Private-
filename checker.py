import json
import os
import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]
SEARCH_URL = "https://www.ragtag.jp/search?q=satisfy"
SEEN_PATH = "seen.json"


def load_seen():
    try:
        with open(SEEN_PATH, "r") as f:
            return set(json.load(f)["ids"])
    except:
        return set()


def save_seen(ids):
    data = {
        "ids": list(ids),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    with open(SEEN_PATH, "w") as f:
        json.dump(data, f)


def extract_item_id(href):
    m = re.search(r"/item/(\d+)", href)
    return m.group(1) if m else None


print("Start Ragtag checker")

r = requests.get(SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"})
print("Status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

items = []

for a in soup.select('a[href*="/item/"]'):
    parent = a.parent

    # SOLD OUT除外
    if parent and "SOLD" in parent.get_text():
        continue

    href = a.get("href")

    item_id = extract_item_id(href)
    if not item_id:
        continue

    title = a.get_text(strip=True)
    url = "https://www.ragtag.jp" + href

    items.append((item_id, title, url))

print("Items found:", len(items))

seen = load_seen()

current_ids = set([i[0] for i in items])

new_ids = current_ids - seen

print("New items:", len(new_ids))

save_seen(current_ids)

for item_id, title, url in items:
    if item_id not in new_ids:
        continue

    message = f"🔥 Satisfy 新着\n{title}\n{url}"

    print("Send:", title)

    requests.post(WEBHOOK, json={"content": message})
