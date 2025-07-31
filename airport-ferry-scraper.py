import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://port.kinmen.gov.tw/kmeis/manager/tmp/realtimeshow1.php"

def get_icon_and_label(status):
    if "安檢" in status:
        return "🟡", "安檢"
    elif "離港" in status:
        return "✅", "離港"
    elif "準時" in status:
        return "🟢", "準時"
    elif "延誤" in status:
        return "🟠", "延誤"
    elif "停航" in status:
        return "⛔", "停航"
    else:
        return "⚪", "狀態未知"

try:
    response = requests.get(URL, verify=False)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("tr")[1:]
except Exception as e:
    print(f"⚠️ 無法取得資料: {e}")
    rows = []

ferries = []

for row in rows:
    cols = row.find_all("td")
    if len(cols) < 6:
        continue

    raw_name = cols[1].get_text(strip=True)
    name = raw_name.split()[0]

    sched = cols[3].get_text(strip=True)
    actual = cols[4].get_text(strip=True) or "--:--"
    status_text = cols[5].get_text(strip=True)

    icon, label = get_icon_and_label(status_text)
    status = f"{icon} {label}"

    ferries.append({
        "name": name,
        "dep": sched,
        "actual": actual,
        "status": status
    })

now = datetime.utcnow() + timedelta(hours=8)

output = {
    "updated": now.strftime("%Y-%m-%d %H:%M:%S"),
    "ferries": ferries
}

output_path = "docs/data/airport-ferry.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("✅ Saved to docs/data/airport-ferry.json")
