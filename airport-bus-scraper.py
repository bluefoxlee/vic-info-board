# airport-bus-scraper-v47.py

import requests
import json
from datetime import datetime

# 金門站牌代碼與對應路線整理
bus_routes = {
    "藍1_山外": ["13", "131"],
    "藍1_金城": ["14", "141"],
    "3": ["31", "32"],
    "27": ["2711", "2721"],
    "35": ["351", "352"],
    "36": ["364"]
}

stop_name = "民航站"

def fetch_estimates(route_ids):
    ids = ",".join(route_ids)
    url = f"https://ebus.kinmen.gov.tw/xmlbus4/GetEstimateTime.json?routeIds={ids}"
    try:
        res = requests.get(url, verify=False, timeout=10)
        data = res.json()
        return data
    except Exception as e:
        print(f"❌ 無法取得資料：{e}")
        return {}

def extract_for_airport(data, label):
    output = []
    for route_id in data:
        for stop in data[route_id]:
            if stop["StopName"] != stop_name:
                continue
            dest = stop.get("GoBackText", "").replace("往", "").strip()
            car_id = stop.get("carId", "—").strip() or "—"
            schedule = stop.get("comeTime", "").strip()
            est_list = stop.get("ests", [])
            if est_list:
                est_info = est_list[0]
                countdown = est_info.get("countdowntime", None)
                eta = f"{round(countdown/60)}分" if countdown is not None else "—"
            else:
                eta = "（預定）" if schedule else "尚無資料"
            output.append({
                "carNo": car_id,
                "route": label,
                "eta": eta,
                "dest": dest,
                "schedule": schedule
            })
    return output

def main():
    print("👀 main() 開始執行")
    all_results = []

    for label, ids in bus_routes.items():
        print(f"🔍 處理 {label}")
        data = fetch_estimates(ids)
        result = extract_for_airport(data, label.split("_")[0])  # 顯示為「藍1」、「3」等
        all_results.extend(result)

    output = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": all_results
    }

    path = "docs/data/airport-bus.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("📁 寫入 airport-bus.json 完成")
    print("✅ airport-bus.json updated")

if __name__ == "__main__":
    main()
