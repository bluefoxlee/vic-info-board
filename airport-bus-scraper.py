import requests
import json
import os
from datetime import datetime

# 停靠民航站且顯示方向為山外的路線
ROUTE_IDS = ["13", "131", "14", "141"]
STOP_NAME = "民航站"
DEST_KEYWORDS = {"13": "山外", "131": "山外", "14": "金城", "141": "金城"}

def fetch_estimate_data():
    url = f"https://ebus.kinmen.gov.tw/xmlbus4/GetEstimateTime.json?routeIds={','.join(ROUTE_IDS)}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching estimate data: {e}")
        return {}

def parse_data(data):
    output = []
    for route_id in ROUTE_IDS:
        stops = data.get(route_id, [])
        for stop in stops:
            stop_name = stop.get("StopName", "")
            go_back = str(stop.get("GoBack", ""))
            if stop_name != STOP_NAME or go_back not in ("1", "2"):
                continue

            # 找出 ests 資料
            ests = stop.get("ests", [])
            if not ests:
                continue

            for est in ests:
                car_no = est.get("carid", "").strip()
                countdown = est.get("est", None)
                schedule = stop.get("comeTime", "") or "--:--"

                if not car_no:
                    continue

                # 判斷方向
                dest = DEST_KEYWORDS.get(route_id, "")
                if not dest:
                    continue

                eta = f"{countdown}分" if isinstance(countdown, int) else "--"

                # 避免重複
                exists = any(x["carNo"] == car_no for x in output)
                if exists:
                    continue

                output.append({
                    "carNo": car_no,
                    "route": "藍1",
                    "eta": eta,
                    "dest": dest,
                    "schedule": schedule,
                })
    return output

def main():
    print("👀 main() 開始執行")
    data = fetch_estimate_data()
    output = parse_data(data)

    os.makedirs("docs/data", exist_ok=True)
    with open("docs/data/airport-bus.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("📁 寫入 docs/data/airport-bus.json 完成")
    print("✅ airport-bus.json updated")

if __name__ == "__main__":
    main()
