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

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 5:
            name = cols[0].text.strip()
            dep = cols[1].text.strip()
            actual = cols[2].text.strip()
            status = cols[3].text.strip()
            ferry_name = row[1].strip()  # 船名
            scheduled_time = row[0].strip()  # 預定出發時間
            actual_time = row[4].strip() if len(row) > 4 and row[4].strip() else "--:--"
            status_text = "準時 On Time" if actual_time == "--:--" else "已離港"

            ferries.append({
                "name": ferry_name,
                "dep": scheduled_time,
                "actual": actual_time,
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
