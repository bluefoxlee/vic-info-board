import requests
import json
import os
from datetime import datetime

STOP_IDS = ["6035", "7947", "12055", "1743", "3333"]
ROUTE_GROUPS = {
    "藍1_山外": ["13", "131"],
    "藍1_金城": ["14", "141"],
    "3": ["31", "32"],
    "27": ["2711", "2721"],
    "35": ["351", "352"],
    "36": ["364"]
}
ROUTE_MAP = {
    "13": {"label": "藍1", "dest": "山外"},
    "131": {"label": "藍1", "dest": "山外"},
    "14": {"label": "藍1", "dest": "金城"},
    "141": {"label": "藍1", "dest": "金城"},
    "31": {"label": "3", "dest": "山外"},
    "32": {"label": "3", "dest": "金城"},
    "2711": {"label": "27", "dest": "沙美"},
    "2721": {"label": "27", "dest": "山外"},
    "351": {"label": "35", "dest": "烈嶼"},
    "352": {"label": "35", "dest": "山外"},
    "364": {"label": "36", "dest": "山外"}
}
OUTPUT_PATH = "docs/data/airport-bus.json"

def fetch_estimates(route_ids):
    url = f"https://ebus.kinmen.gov.tw/xmlbus4/GetEstimateTime.json?routeIds={','.join(route_ids)}"
    print(f"📥 Fetching: {url}")
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return {}

def parse_estimates(group_name, route_ids, data):
    result = []
    for rid in route_ids:
        stops = data.get(rid, [])
        for stop in stops:
            sid = str(stop.get("SID", ""))
            if sid not in STOP_IDS:
                continue

            route_info = ROUTE_MAP.get(rid)
            if not route_info:
                continue

            label = route_info["label"]
            dest = route_info["dest"]
            car_no = stop.get("comeCarid") or stop.get("carId") or "—"
            schedule = stop.get("comeTime", "").strip()
            ests = stop.get("ests", [])
            eta = "（預定）" if schedule and not ests else "尚無資料"

            if ests:
                first_est = ests[0]
                if first_est.get("est") is not None:
                    eta = f"{first_est['est']}分"

            result.append({
                "carNo": car_no,
                "route": label,
                "eta": eta,
                "dest": dest,
                "schedule": schedule
            })

    return result

def remove_duplicates(data):
    seen = set()
    unique = []
    for entry in data:
        key = (entry["carNo"], entry["route"], entry["dest"], entry["schedule"])
        if key not in seen:
            seen.add(key)
            unique.append(entry)
    return unique

def main():
    print("👀 main() 開始執行")
    output = []
    for group_name, route_ids in ROUTE_GROUPS.items():
        print(f"🔍 處理 {group_name}")
        data = fetch_estimates(route_ids)
        results = parse_estimates(group_name, route_ids, data)
        output.extend(results)

    output = remove_duplicates(output)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output.append({"updated": now})

    os.makedirs("docs/data", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("📁 寫入 airport-bus.json 完成")
    print("✅ airport-bus.json updated")
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
