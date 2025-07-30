import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

URL = "https://port.kinmen.gov.tw/kmeis/manager/tmp/realtimeshow1.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

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

def fetch_ferry_data():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10, verify=False)
        response.encoding = "utf-8"  # 確保中文字不亂碼
    except Exception as e:
        print(f"❌ Failed to fetch data: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table tr")[1:]  # 跳過表頭

    ferry_data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        name = cols[1].text.strip()
        scheduled_time = cols[2].text.strip()
        actual_time = cols[3].text.strip()
        status_raw = cols[4].text.strip()
        status = status_raw.split()[0] if status_raw else "未知"

        if actual_time == "":
            actual_time = "--:--"
            status = "準時"

        ferry_data.append({
            "name": name,
            "dep": scheduled_time,
            "actual": actual_time,
            "status": f"{get_icon(status)} {status}"
        })

    return ferry_data

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    ferries = fetch_ferry_data()

    # ➕ 台灣時間：UTC+8
    now = datetime.utcnow() + timedelta(hours=8)

    result = {
        "updated": now.strftime("%Y-%m-%d %H:%M:%S"),
        "ferries": ferries
    }

    save_json(result, "docs/data/airport-ferry.json")
    print("✅ Saved to docs/data/airport-ferry.json")

if __name__ == "__main__":
    main()
