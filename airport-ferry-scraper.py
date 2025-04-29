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
    name = tds[1].text.strip()            # 船名
    dep = tds[3].text.strip()             # ✅ 預定時間（原定開航）
    actual = tds[4].text.strip()          # ✅ 實際時間
    status = tds[5].text.strip()          # ✅ 狀態：安檢中／離港／延誤

    ferries.append({
        "name": name,
        "dep": dep,
        "actual": actual,
        "status": status
    })

os.makedirs("docs/data", exist_ok=True)
with open("docs/data/airport-ferry.json", "w", encoding="utf-8") as f:
    json.dump({
        "updated": datetime.now().isoformat(),
        "ferries": ferries
    }, f, ensure_ascii=False, indent=2)
