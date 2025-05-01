
from datetime import datetime, timedelta, timezone
import requests
import json
import os

routes_info = {
    "13": {"label": "藍1", "direction": "往山外"},
    "131": {"label": "藍1", "direction": "往山外"},
    "14": {"label": "藍1", "direction": "往金城"},
    "141": {"label": "藍1", "direction": "往金城"},
    "31": {"label": "3", "direction": "往山外"},
    "32": {"label": "3", "direction": "往金城"},
    "2711": {"label": "27", "direction": "往沙美"},
    "2721": {"label": "27", "direction": "往山外"},
    "351": {"label": "35", "direction": "往烈嶼"},
    "352": {"label": "35", "direction": "往山外"},
    "364": {"label": "36", "direction": "往山外"},
}

def fetch_estimates():
    all_est = []
    route_ids = ",".join(routes_info.keys())
    url = f"https://ebus.kinmen.gov.tw/xmlbus4/GetEstimateTime.json?routeIds={route_ids}"
    try:
        res = requests.get(url, verify=False, timeout=10)
        data = res.json()
        for rid, stop_list in data.items():
            for stop in stop_list:
                if "民航站" not in stop.get("StopName", ""):
                    continue
                stop["RouteID"] = rid
                all_est.append(stop)
    except Exception as e:
        print("❌ ETA 抓取錯誤：", e)
    return all_est

def main():
    print("👀 main() 開始執行")
    est = fetch_estimates()
    print(f"📦 預估資料數量：{len(est)}")

    buses = []
    valid_count = 0
    
    for s in est:
        route_id = s.get("RouteID", "")
        direction = direction_map.get(route_id, "").replace("往", "")

        if not s.get("ests"):
            eta = "尚無資料"
            car_no = "—"
        else:
            eta = extract_eta(s["ests"])
            car_no = s.get("carId", "—")

        schedule_time = s.get("schedule_time", "")
        buses.append({
            "carNo": car_no,
            "route": friendly_route(route_id),
            "schedule": schedule_time,
            "eta": eta if eta else f"{schedule_time}（預定）",
            "dest": direction
        })
        route_id = s.get("RouteID", "")
        direction = direction_map.get(route_id, "")
        if direction.startswith("往"):
            direction = direction.replace("往", "")
        schedule_time = s.get("schedule_time", "")
        eta = extract_eta(s.get("ests", []))

        buses.append({
            "carNo": car_no,
            "route": friendly_route(route_id),
            "schedule": schedule_time,
            "eta": eta if eta else f"{schedule_time}（預定）",
            "dest": direction
        })
            continue

        if not s.get("ests"):
            buses.append({
                "carNo": "—",
                "route": routes_info.get(s.get("RouteID", ""), {}).get("label", "❓"),
                "eta": "尚無資料",
                "dest": routes_info.get(s.get("RouteID", ""), {}).get("direction", "❓")
            })
            continue  # ❗ 跳過 est_entry 處理

        for est_entry in s.get("ests", []):
            car_id = est_entry.get("carid", "🚍")
            est_min = est_entry.get("est")
            buses.append({
                "carNo": car_id,
                "route": routes_info.get(s.get("RouteID", ""), {}).get("label", "❓"),
                "eta": f"{est_min}分" if est_min is not None else "未發車",
                "dest": routes_info.get(s.get("RouteID", ""), {}).get("direction", "❓")
            })

    now = datetime.now(timezone(timedelta(hours=8)))
    output = {
        "buses": buses,
        "updated": now.strftime("%Y-%m-%d %H:%M:%S")
    }

    os.makedirs("docs/data", exist_ok=True)
    with open("docs/data/airport-bus.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("📁 寫入 airport-bus.json 完成")
    print("✅ airport-bus.json updated")
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
