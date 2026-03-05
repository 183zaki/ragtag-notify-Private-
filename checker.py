import requests
from bs4 import BeautifulSoup
import os

WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]

URL = "https://www.ragtag.jp/search?q=satisfy"

print("Start Ragtag checker")

r = requests.get(URL)
print("Status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

items = soup.select(".item")

print("Items found:", len(items))

if items:
    first = items[0]
    title = first.select_one(".item_name").text.strip()
    link = "https://www.ragtag.jp" + first.select_one("a")["href"]

    message = f"🔥 Ragtag New Item\n{title}\n{link}"

    print("Sending to Discord:", title)

    requests.post(WEBHOOK, json={"content": message})
