import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz
from pathlib import Path

url = "https://port.kinmen.gov.tw/kmeis/manager/tmp/realtimeshow1.php"

try:
    response = requests.get(url, timeout=10)
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("tr")[1:]  # skip header

    ferries = []
except Exception as e:
    print("❌ 無法取得網頁資料:", e)
    rows = []
    ferries = []

    from datetime import datetime, timedelta

now = datetime.now()
time_window_start = now - timedelta(hours=1)
time_window_end = now + timedelta(hours=2)

for row in rows:
    cols = row.find_all("td")
    if len(cols) >= 5:
        scheduled_time = cols[1].text.strip()  # 預定時間
        raw_ferry_name = cols[2].text.strip()  # 船名（含英文）
        actual_time = cols[3].text.strip()     # 實際出發時間
        status_text = "已離港" if actual_time else "準時 On Time"

        # 去除英文簡寫
        ferry_name = raw_ferry_name.split()[0]

        try:
            sched_dt = datetime.strptime(scheduled_time, "%H:%M")
            sched_dt = sched_dt.replace(year=now.year, month=now.month, day=now.day)
        except ValueError:
            continue

        if time_window_start <= sched_dt <= time_window_end:
            ferries.append({
                "name": ferry_name,
                "dep": scheduled_time,
                "actual": actual_time or "--:--",
                "status": status_text
            })

    if not ferries:
        ferries = [{"note": "⚠️ 無法取得船班資料，可能為深夜或網站無回應"}]

except Exception as e:
    ferries = [{"note": "⚠️ 無法取得船班資料，可能為深夜或網站無回應"}]

updated_time = datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S")

output = {
    "ferries": ferries,
    "updated": updated_time
}

Path("docs/data/airport-ferry.json").write_text(json.dumps(output, ensure_ascii=False, indent=2))
print("✅ Saved to docs/data/airport-ferry.json")
