import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

url = "https://port.kinmen.gov.tw/kmeis/manager/tmp/realtimeshow1.php"
response = requests.get(url)
response.encoding = "utf-8"
soup = BeautifulSoup(response.text, "html.parser")

now = datetime.now()
start_time = now - timedelta(hours=1)
end_time = now + timedelta(hours=3)

rows = soup.find_all("tr")[1:]
ferries = []

def parse_time_str(tstr):
    try:
        return datetime.strptime(tstr.strip(), "%H:%M").replace(
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

for row in rows:
    cols = row.find_all("td")
    if len(cols) < 5:
        continue

    raw_name = cols[2].get_text(strip=True)           # 船名（含英文）
    name = raw_name.split()[0]                        # 去除英文簡寫
    sched = cols[1].get_text(strip=True)              # 預定時間
    sched_time = parse_time_str(sched)
    if sched_time is None or not (start_time <= sched_time <= end_time):
        continue

    actual = cols[3].get_text(strip=True)             # 實際時間
    status_text = cols[4].get_text(strip=True)        # 狀態說明
    icon = get_icon(status_text)

    ferries.append({
        "name": name,
        "sched": sched,
        "actual": actual if actual else "--:--",
        "icon": icon
    })

html_parts = []
html_parts.append("""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <style>
    body {
      margin: 0;
      font-family: monospace;
      font-size: 1.2em;
      color: yellow;
      text-shadow: 2px 2px 4px black;
      background-color: transparent;
    }
    .ferry-container {
      background: rgba(0, 0, 0, 0.6);
      padding: 10px;
      border-radius: 10px;
    }
    .ferry-line {
      display: flex;
      justify-content: space-between;
      padding: 4px 0;
    }
    .ferry-separator {
      border-top: 1px solid yellow;
      margin: 4px 0;
    }
    .col-name { width: 8em; }
    .col-time { width: 10em; text-align: center; }
    .col-icon { width: 2em; text-align: right; }
  </style>
</head>
<body>
  <div class="ferry-container">
""")

for idx, f in enumerate(ferries):
    html_parts.append(
        f"""    <div class="ferry-line">
      <div class="col-name">{f['name']}</div>
      <div class="col-time">{f['sched']} - {f['actual']}</div>
      <div class="col-icon">{f['icon']}</div>
    </div>"""
    )
    if idx < len(ferries) - 1:
        html_parts.append('    <div class="ferry-separator"></div>')

html_parts.append("""  </div>
</body>
</html>""")

html = "\n".join(html_parts)

with open("ferry.html", "w", encoding="utf-8") as f:
    f.write(html)
print("ferry.html 已產生")

output = {
    "ferries": ferries,
    "updated": now.strftime("%Y-%m-%d %H:%M:%S")
}

import json
with open("airport-ferry.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
