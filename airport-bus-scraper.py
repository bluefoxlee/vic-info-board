# Kinmen-Bus-Info-Airport.py
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import urllib3
urllib3.disable_warnings()

routes_info = {
    "13": {"label": "藍1", "direction": "往山外", "group": "blue1-s"},
    "131": {"label": "藍1", "direction": "往山外", "group": "blue1-s"},
    "14": {"label": "藍1", "direction": "往金城", "group": "blue1-j"},
    "141": {"label": "藍1", "direction": "往金城", "group": "blue1-j"},
    "31": {"label": "3", "direction": "往山外", "group": "3-s"},
    "32": {"label": "3", "direction": "往金城", "group": "3-j"},
    "2711": {"label": "27", "direction": "往沙美", "group": "27-s"},
    "2721": {"label": "27", "direction": "往山外", "group": "27-w"},
    "351": {"label": "35", "direction": "往烈嶼", "group": "35-l"},
    "352": {"label": "35", "direction": "往山外", "group": "35-w"},
    "364": {"label": "36", "direction": "往山外", "group": "36-w"},
}

# 日期與 API
today = datetime.now()
today_str = today.strftime("%Y-%-m-%d")
base_url = "https://ebus.kinmen.gov.tw"
estimate_url_template = base_url + "/xmlbus4/GetEstimateTime.json?routeIds={}"
schedule_url = f"{base_url}/api/schedule?date={today_str}"

# 取得表定資料
scheduled_cars = defaultdict(list)
try:
    schedule_data = requests.get(schedule_url, verify=False).json()
    for item in schedule_data:
        rid = item["route_id"]
        if rid not in routes_info:
            continue
        schedule_time = item["schedule_time"]
        car_id = item.get("car", {}).get("id", "🚍")
        dt = datetime.strptime(f"{today_str} {schedule_time}", "%Y-%m-%d %H:%M")
        if dt >= today:
            scheduled_cars[rid].append({
                "car_id": car_id,
                "schedule": schedule_time,
                "dt": dt
            })
except Exception as e:
    print("❌ 表定 API 錯誤：", e)

# 即時預估
results = []
for rid in routes_info:
    try:
        url = estimate_url_template.format(rid)
        res = requests.get(url, verify=False)
        data = res.json().get(rid, [])
        for stop in data:
            if "民航站" not in stop.get("StopName", ""):
                continue
            for est in stop.get("ests", []):
                est_min = est.get("est")
                car_id = est.get("carid", "🚍")
                eta = today + timedelta(minutes=est_min if est_min else 9999)
                results.append({
                    "route_id": rid,
                    "label": routes_info[rid]["label"],
                    "direction": routes_info[rid]["direction"],
                    "group": routes_info[rid]["group"],
                    "car_id": car_id,
                    "status": f"{est_min}分" if est_min is not None else "未發車",
                    "time_order": eta
                })
    except:
        continue

# 加上預定班次
for rid, cars in scheduled_cars.items():
    for sched in cars:
        results.append({
            "route_id": rid,
            "label": routes_info[rid]["label"],
            "direction": routes_info[rid]["direction"],
            "group": routes_info[rid]["group"],
            "car_id": sched["car_id"],
            "status": f"未發車（預定 {sched['schedule']}）",
            "time_order": sched["dt"]
        })

# 分組後只保留一筆
grouped = {}
for r in sorted(results, key=lambda x: x["time_order"]):
    if x := grouped.get(r["group"]):
        continue
    grouped[r["group"]] = r

# 組出 HTML 表格
lines = ['<meta charset="utf-8"><style>body{font-family:sans-serif;font-size:18px}</style><div>']
for row in grouped.values():
    line = f'{row["car_id"]}｜{row["label"]}｜{row["status"]}｜{row["direction"]}'
    lines.append(f"<div>🚌 {line}</div>")
lines.append("</div>")

# 寫入檔案
with open("airport_bus_info.html", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("✅ 已輸出 airport_bus_info.html")

# 濾除晚上七點（含）以後的班次
results = [b for b in results if b["time_order"].hour < 19]

# 分組取每個 group 的第一筆資料（最近一班）
seen = set()
filtered = []
for b in sorted(results, key=lambda x: x["time_order"]):
    key = (b["group"])
    if key not in seen:
        seen.add(key)
        filtered.append(b)
results = filtered

# 匯出為 HTML，使用 ferry-style 統一樣式
html_parts = []
html_parts.append("""<!DOCTYPE html>
<html lang='zh-TW'>
<head>
  <meta charset='UTF-8'>
  <style>
    body {
      margin: 0;
      font-family: monospace;
      font-size: 1.2em;
      color: yellow;
      text-shadow: 2px 2px 4px black;
      background-color: transparent;
    }
    .bus-container {
      background: rgba(0, 0, 0, 0.6);
      padding: 10px;
      border-radius: 10px;
    }
    .bus-line {
      display: flex;
      justify-content: space-between;
      padding: 4px 0;
    }
    .bus-separator {
      border-top: 1px solid yellow;
      margin: 4px 0;
    }
    .col-id { width: 10em; }
    .col-time { width: 14em; text-align: center; }
    .col-direction { flex-grow: 1; text-align: right; }
  </style>
</head>
<body>
  <div class='bus-container'>
""")

for idx, b in enumerate(results):
    time_str = b.get("status", "--").replace(" ", "")
    if "未發車（預定" in time_str:
        time_str = time_str.replace("未發車（預定", "").replace("）", "發車")
    if time_str.endswith("分") and not time_str.endswith("分鐘"):
        time_str = time_str.replace("分", "分鐘")
    car_id = b.get("car_id", "🚍")
    if car_id == "🚍":
        car_id = "🚍------"
    label = b.get("label", "--")
    direction = b.get("direction", "")
    html_parts.append(f"""    <div class='bus-line'>
      <div class='col-id'>{car_id}｜{label}</div>
      <div class='col-time'>{time_str}</div>
      <div class='col-direction'>{direction}</div>
    </div>""")
    if idx < len(results) - 1:
        html_parts.append("    <div class='bus-separator'></div>")

html_parts.append("""  </div>
</body>
</html>""")

html = "\n".join(html_parts)
with open("bus.html", "w", encoding="utf-8") as f:
    f.write(html)
print("bus.html 已產生")
