import requests
from bs4 import BeautifulSoup
import os

WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]

URL = "https://www.ragtag.jp/search?q=satisfy"

print("Start Ragtag checker")

r = requests.get(URL)
print("Status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

items = soup.select("li")

print("Items found:", len(items))

for item in items[:5]:
    a = item.find("a")
    if not a:
        continue

    title = a.get_text(strip=True)
    link = a["href"]

    if "/item/" in link:
        url = "https://www.ragtag.jp" + link
        message = f"🔥 Ragtag Item\n{title}\n{url}"

        print("Sending:", title)

        requests.post(WEBHOOK, json={"content": message})
        break
