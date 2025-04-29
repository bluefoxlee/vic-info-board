from datetime import datetime, timedelta
from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup
import pytz
from pathlib import Path

URL = "https://port.kinmen.gov.tw/kmeis/manager/tmp/realtimeshow1.php"

def get_now():
    return datetime.now(pytz.timezone("Asia/Taipei"))

def parse_time(tstr):
    try:
        return datetime.strptime(tstr, "%H:%M").time()
    except:
        return None

def scrape_ferry_data():
    try:
        response = requests.get(URL, timeout=10)
        response.encoding = "utf-8"
    except Exception:
        return [{
            "note": "⚠️ 無法取得船班資料，可能為深夜或網站無回應"
        }]

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="real")
    if not table:
        return [{"note": "⚠️ 網站格式異常，無法擷取資料"}]

    rows = table.find_all("tr")[1:]
    now = get_now()
    today = now.date()

    all_ferries = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        name = cols[1].get_text(strip=True)
        dep = cols[3].get_text(strip=True)
        actual = cols[4].get_text(strip=True)
        status = cols[5].get_text(strip=True)

        # 優先用 actual，再用 dep 來判斷時間
        use_time_str = actual if actual != "--:--" else dep
        use_time = parse_time(use_time_str)
        if not use_time:
            continue

        dt_time = datetime.combine(today, use_time).replace(tzinfo=pytz.timezone("Asia/Taipei"))

        all_ferries.append({
            "name": name,
            "dep": dep,
            "actual": actual,
            "status": status,
            "time_obj": dt_time  # 加上 datetime 方便排序和比較
        })

    if not all_ferries:
        return [{"note": "⚠️ 資料解析失敗，找不到任何船班"}]

    all_ferries.sort(key=lambda x: x["time_obj"])

    # 篩選三種情況
    filtered = []
    lower = now - timedelta(hours=1)
    upper = now + timedelta(hours=2)

    for ferry in all_ferries:
        if lower <= ferry["time_obj"] <= upper:
            filtered.append({k: ferry[k] for k in ["name", "dep", "actual", "status"]})

    if filtered:
        return filtered

    if now < all_ferries[0]["time_obj"]:
        # 顯示最早三班
        return [
            {k: ferry[k] for k in ["name", "dep", "actual", "status"]}
            for ferry in all_ferries[:3]
        ]

    if now > all_ferries[-1]["time_obj"]:
        # 顯示最後一班 + 末班船提示
        last = {k: all_ferries[-1][k] for k in ["name", "dep", "actual", "status"]}
        return [last, {"note": "末班船已離港"}]

    return [{"note": "⚠️ 目前無符合時間範圍的船班"}]

output = {
    "ferries": scrape_ferry_data(),
    "updated": get_now().strftime("%Y-%m-%d %H:%M:%S")
}

Path("docs/data/airport-ferry.json").write_text(json.dumps(output, ensure_ascii=False, indent=2))
