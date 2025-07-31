import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Referer": "https://port.kinmen.gov.tw/"
}
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

def fetch_ferry_data():
    try:
        res = requests.get(URL, headers=headers, timeout=10, verify=False)
        res.encoding = "utf-8"  # 正確設定編碼
        soup = BeautifulSoup(res.text, "html.parser")

        table = soup.find("table")
        rows = table.find_all("tr")[1:]  # skip header row

        ferry_data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 6:
                continue

            name = cols[1].text.strip()
            scheduled_time = cols[2].text.strip()
            actual_time = cols[3].text.strip()
            status_raw = cols[4].text.strip()

            if actual_time == "":
                actual_time = "--:--"
                status = "準時"
            else:
                status = "離港"

            ferry_data.append({
                "name": name,
                "dep": scheduled_time,
                "actual": actual_time,
                "status": f"{get_icon(status)} {status}"
            })

        return ferry_data

    except Exception as e:
        print("⚠️ 無法取得資料:", e)
        return []

def main():
    ferries = fetch_ferry_data()

    # 使用台灣時區（+8）
    now = datetime.utcnow() + timedelta(hours=8)

    output = {
        "updated": now.strftime("%Y-%m-%d %H:%M:%S"),
        "ferries": ferries
    }

    with open("docs/data/airport-ferry.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("✅ Saved to docs/data/airport-ferry.json")

if __name__ == "__main__":
    main()
