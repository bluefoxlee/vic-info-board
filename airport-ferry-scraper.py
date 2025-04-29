import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

url = "https://port.kinmen.gov.tw/kmeis/manager/tmp/realtimeshow1.php"
headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_ferry_data():
    try:
        res = requests.get(url, timeout=10)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")

        rows = soup.select("table")[0].select("tr")[1:]  # 跳過表頭
        ferries = []
        for row in rows:
            cols = row.select("td")
            if len(cols) < 6:
                continue
            name = cols[0].text.strip().split()[0]
            dep = cols[1].text.strip()
            actual = cols[2].text.strip()
            status = cols[5].text.strip()

            ferries.append({
                "name": name,
                "dep": dep,
                "actual": actual,
                "status": status
            })

        return ferries

    except Exception:
        return None

def filter_ferries(ferries):
    now = datetime.now()
    current_time = now.time()

    # 判斷是否在午夜至首航前
    earliest_time = None
    valid_ferries = []
    for f in ferries:
        try:
            dep_time = datetime.strptime(f["dep"], "%H:%M").time()
            if earliest_time is None or dep_time < earliest_time:
                earliest_time = dep_time
        except:
            continue

    if earliest_time and current_time < earliest_time:
        # 尚未開始營運，顯示最早的 3 班
        return ferries[:3]

    # 篩選前 1 小時 ~ 後 2 小時
    result = []
    for f in ferries:
        try:
            dep_datetime = datetime.combine(now.date(), datetime.strptime(f["dep"], "%H:%M").time())
            time_diff = (dep_datetime - now).total_seconds() / 60
            if -60 <= time_diff <= 120:
                result.append(f)
        except:
            continue
    return result

ferries = get_ferry_data()
output = {}

if ferries is None:
    output["ferries"] = [{
        "note": "⚠️ 無法取得船班資料，可能為深夜或網站無回應"
    }]
else:
    filtered = filter_ferries(ferries)
    if not filtered:
        output["ferries"] = [{
            "note": "⚠️ 目前無符合時間範圍的船班"
        }]
    else:
        output["ferries"] = filtered

output["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open("docs/data/airport-ferry.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
