# airport-bus-scraper-v46.py

import requests
import json
import os
from datetime import datetime

GROUPS = [
    {"ids": ["13", "131"], "label": "藍1", "dest": "山外"},
    {"ids": ["14", "141"], "label": "藍1", "dest": "金城"},
    {"ids": ["31", "32"], "label": "3", "dest": ""},
    {"ids": ["2711", "2721"], "label": "27", "dest": ""},
    {"ids": ["351", "352"], "label": "35", "dest": ""},
    {"ids": ["364"], "label": "36", "dest": ""}
]

STOP_NAME = "民航站"

def fetch_data(route_ids):
    url = f"https://ebus.kinmen.gov.tw/xmlbus4/GetEstimateTime.json?routeIds={','.join(route_ids)}"
    print(f"📥 Fetching: {url}")
    try:
        response = requests.get(url, verify=False, timeout=15)
        return response.json()
    except Exception as e:
        print(f"⚠️ 無法取得資料: {e}")
        return {}

def process_group(group):
    raw_data = fetch_data(group["ids"])
    results = []

    for route_id in raw_data:
        stops = raw_data[route_id]
        for stop in stops:
            if stop.get("StopName") != STOP_NAME:
                continue
            car_no = stop.get("comeCarid") or stop.get("carId") or "—"
            ests = stop.get("ests", [])
            come_time = stop.get("comeTime", "")
            eta = ""
            if ests and isinstance(ests, list) and ests[0].get("est") is not None:
                eta = f"{ests[0]['est']}分"
            elif come_time and car_no != "—":
                eta = "（預定）"
            else:
                eta = "尚無資料"

            result = {
                "carNo": car_no,
                "route": group["label"],
                "eta": eta,
                "dest": group["dest"] or stop.get("GoBackName", ""),
                "schedule": come_time
            }
            results.append(result)

    return results

def main():
    print("👀 main() 開始執行")
    all_results = []

    for group in GROUPS:
        print(f"🔍 處理 {group['label']}_{group['dest'] or ''}".strip("_"))
        group_result = process_group(group)
        all_results.extend(group_result)

    all_results.append({
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    os.makedirs("docs/data", exist_ok=True)
    with open("docs/data/airport-bus.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print("✅ airport-bus.json updated")

if __name__ == "__main__":
    main()
