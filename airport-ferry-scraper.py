import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

URL = "https://port.kinmen.gov.tw/kmeis/manager/tmp/realtimeshow1.php"

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

try:
    response = requests.get(URL, verify=False, timeout=10)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
except Exception:
    print("❌ 無法取得資料")
    exit()

rows = soup.find_all("tr")[1:]
now = datetime.now()
window_start = now - timedelta(hours=1)
window_end = now + timedelta(hours=2)

result = []

for row in rows:
    cols = row.find_all("td")
    if len(cols) < 6:
        continue

    dep_time_str = cols[0].text.strip()[:5]
    name = cols[1].text.strip().split(" ")[0]  # 去除英文
    destination = cols[2].text.strip()
    schedule_time = cols[3].text.strip()[:5]
    actual_time = cols[4].text.strip()[:5]
    status_raw = cols[5].text.strip()

    # 預定時間
    try:
        dep_time = datetime.strptime(dep_time_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
    except:
        continue

    # 若跨日修正
    if dep_time < window_start:
        dep_time += timedelta(days=1)

    if window_start <= dep_time <= window_end:
        status = (
            "已離港" if "離港" in status_raw
            else "準時" if "準時" in status_raw
            else "延誤" if "延誤" in status_raw
            else "安檢中" if "安檢" in status_raw
            else "停航" if "停航" in status_raw
            else status_raw
        )

        actual_display = actual_time if actual_time else "--:--"

        result.append({
            "name": name,
            "dep": schedule_time,
            "actual": actual_display,
            "status": status,
            "icon": get_icon(status)
        })

print(f"✅ 篩選後共 {len(result)} 筆")

with open("docs/data/airport-ferry.json", "w", encoding="utf-8") as f:
    json.dump({"updated": now.strftime("%Y-%m-%d %H:%M:%S"), "ferries": result}, f, ensure_ascii=False, indent=2)
