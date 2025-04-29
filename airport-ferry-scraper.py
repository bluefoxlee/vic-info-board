import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

url = "https://port.kinmen.gov.tw/kmeis/manager/tmp/realtimeshow1.php"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

ferries = []

try:
    res = requests.get(url, headers=headers, timeout=10)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, "html.parser")
    
    rows = soup.select("table.table tr")[1:]  # skip header
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 4:
            name = cols[0].text.strip()
            dep = cols[1].text.strip()
            actual = cols[2].text.strip()
            status = cols[3].text.strip()
            ferries.append({
                "name": name,
                "dep": dep,
                "actual": actual,
                "status": status
            })
    
    if not ferries:
        raise ValueError("無資料")

except Exception as e:
    ferries = [{
        "note": "⚠️ 無法取得船班資料，可能為深夜或網站無回應"
    }]

output = {
    "ferries": ferries,
    "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

with open("docs/data/airport-ferry.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("✅ 已更新 docs/data/airport-ferry.json")
