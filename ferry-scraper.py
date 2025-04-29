import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

url = "https://port.kinmen.gov.tw/kmeis/manager/tmp/realtimeshow1.php"
res = requests.get(url, timeout=10)
res.encoding = "utf-8"
soup = BeautifulSoup(res.text, "html.parser")

rows = soup.select("tr")
ferries = []

for row in rows[1:]:
    tds = row.select("td")
    if len(tds) < 6:
        continue
    name = tds[1].text.strip()
    dep = tds[2].text.strip()
    actual = tds[3].text.strip()
    status = tds[4].text.strip()
    ferries.append({
        "name": name,
        "dep": dep,
        "actual": actual,
        "status": status
    })

with open("data/ferry.json", "w", encoding="utf-8") as f:
    json.dump({
        "updated": datetime.now().isoformat(),
        "ferries": ferries
    }, f, ensure_ascii=False, indent=2)