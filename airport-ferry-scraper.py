import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

def parse_time_str(tstr):
    try:
        return datetime.strptime(tstr.strip(), "%H:%M").replace(tzinfo=now.tzinfo, 
            year=now.year, month=now.month, day=now.day
        )
    except:
        return None

def get_icon(status):
    if "安檢" in status:
        return "🟡"
    elif "離港" in status:
        return "✅"
    elif "準時" in status:
        return "🟢"
    elif "延誤" in status:
        return "🟠"
    elif "停航" in status:
        return "⛔"
    else:
        return "⚪"

from datetime import timezone
now = datetime.now(timezone(timedelta(hours=8)))
start_time = now - timedelta(hours=1)
end_time = now + timedelta(hours=2)

try:
    response = requests.get("https://port.kinmen.gov.tw/kmeis/manager/tmp/realtimeshow1.php", timeout=10)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("tr")[1:]
except:
    print("❌ 無法取得資料")
    rows = []

ferries = []

for row in rows:
    cols = row.find_all("td")
    if len(cols) < 6:
        continue

    raw_name = cols[1].get_text(strip=True)
    name = raw_name.split()[0]
    sched = cols[3].get_text(strip=True)
    sched_time = parse_time_str(sched)
    if sched_time is None or not (start_time <= sched_time <= end_time):
        continue

    actual = cols[4].get_text(strip=True)
    status_text = cols[5].get_text(strip=True)
    icon = get_icon(status_text)

    ferries.append({
        "name": name,
        "sched": sched,
        "actual": actual if actual else "--:--",
        "icon": icon
    })

output = {
    "ferries": ferries,
    "updated": now.strftime("%Y-%m-%d %H:%M:%S")
}

with open("docs/data/airport-ferry.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
