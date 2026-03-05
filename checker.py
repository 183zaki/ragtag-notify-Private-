import requests
from bs4 import BeautifulSoup
import os

WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]

URL = "https://www.ragtag.jp/search?q=satisfy"

r = requests.get(URL)
soup = BeautifulSoup(r.text, "html.parser")

items = soup.select(".item")

if items:
    first = items[0]
    title = first.select_one(".item_name").text.strip()
    link = "https://www.ragtag.jp" + first.select_one("a")["href"]

    message = f"🔥 Ragtag New Item\n{title}\n{link}"

    requests.post(WEBHOOK, json={"content": message})
