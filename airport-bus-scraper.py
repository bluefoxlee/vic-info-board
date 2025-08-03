# airport-bus-scraper-v48.py
from datetime import datetime
import requests
import json
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

STOP_NAME = "民航站"

ROUTES = {
    "藍1_山外": ["13", "131"],
    "藍1_金城": ["14", "141"],
    "3": ["31", "32"],
    "27": ["2711", "2721"],
    "35": ["351", "352"],
    "36": ["364"],
}

DEST_MAPPING = {
    "藍1_山外": "山外",
    "藍1_金城": "金城",
    "3": ["山外", "金城"],
    "27": ["沙美", "山外"],
    "35": ["烈嶼", "山外"],
    "36": "山外",
}

def fetch_estimates(route_ids):
    url = f"https://ebus.kinmen.gov.tw/xmlbus4/GetEstimateTime.json?routeIds={','.join(route_ids)}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"❌ Error fetching {route_ids}: {e}")
    return {}

def parse_bus_data():
    result = []

    for route_label, route_ids in ROUTES.items():
        print(f"🔍 處理 {route_label}")
        data = fetch_estimates(route_ids)

        for rid in route_ids:
            stops = data.get(rid, [])
            for stop in stops:
                if stop.get("StopName") != STOP_NAME:
                    continue

                car_no = stop.get("carId", "—")
                ests = stop.get("ests", [])
                come_time = stop.get("comeTime", "")
                eta = ""

                if ests and isinstance(ests, list) and "countdowntime" in ests[0]:
                    mins = round(ests[0]["countdowntime"] / 60)
                    eta = f"{mins}分"
                elif come_time:
                    eta = "（預定）"
                else:
                    eta = "尚無資料"

                schedule = come_time if eta == "（預定）" else ""

                # 顯示路線名稱
                if "藍1" in route_label:
                    route_display = "藍1"
                    dest = DEST_MAPPING[route_label]
                elif route_label == "3":
                    route_display = "3"
                    dest = DEST_MAPPING["3"][0 if "金城" in stop.get("comeTime", "") else 1]
                else:
                    route_display = route_label
                    dest_opts = DEST_MAPPING.get(route_label, "")
                    dest = dest_opts[0] if isinstance(dest_opts, list) else dest_opts

                result.append({
                    "carNo": car_no,
                    "route": route_display,
                    "eta": eta,
                    "dest": dest,
                    "schedule": schedule
                })

    return result

def main():
    print("👀 main() 開始執行")
    buses = parse_bus_data()
    output = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "buses": buses
    }

    os.makedirs("docs/data", exist_ok=True)
    with open("docs/data/airport-bus.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("✅ airport-bus.json updated")

if __name__ == "__main__":
    main()
