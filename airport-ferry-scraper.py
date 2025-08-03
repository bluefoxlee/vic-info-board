from pathlib import Path
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import json
import urllib3

# 設定台灣時區的現在時間
now = datetime.utcnow() + timedelta(hours=8)
start_time = now - timedelta(hours=1)
end_time = now + timedelta(hours=2)

# 狀態圖示
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

# 解析時間字串
def parse_time_str(tstr):
    try:
        return datetime.strptime(tstr.strip(), "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
    except:
        return None

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 抓取網頁
url = "https://port.kinmen.gov.tw/kmeis/manager/tmp/realtimeshow1.php"
try:
    response = requests.get(url, verify=False, timeout=10)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.find_all("tr")

    ferries = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        raw_name = cols[1].get_text(strip=True)
        name = raw_name.split()[0]  # 移除英文簡寫

        sched = cols[3].get_text(strip=True)
        sched_time = parse_time_str(sched)
        if sched_time is None or not (start_time <= sched_time <= end_time):
            continue

        actual = cols[4].get_text(strip=True)
        status_text = cols[5].get_text(strip=True)
        icon = get_icon(status_text)
        status_text_clean = status_text.strip()
        if "已離港" in status_text_clean:
            status_text_clean = "離港"
        elif "安檢" in status_text_clean:
            status_text_clean = "安檢"
        elif "準時" in status_text_clean:
            status_text_clean = "準時"
        elif "延誤" in status_text_clean:
            status_text_clean = "延誤"
        elif "停航" in status_text_clean:
            status_text_clean = "停航"
        else:
            status_text_clean = "狀態未知"
            
        status = f"{get_icon(status_text_clean)} {status_text_clean}"  # 只取「離港」、「安檢」等兩字

        ferries.append({
            "name": name,
            "dep": sched,
            "actual": actual if actual else "--:--",
            "status": status
        })

    result = {
        "updated": now.strftime("%Y-%m-%d %H:%M:%S"),
        "ferries": ferries
    }

    Path("docs/data/airport-ferry.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print("✅ Saved to docs/data/airport-ferry.json")

except Exception as e:
    print(f"⚠️ 無法取得資料: {e}")
