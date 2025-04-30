import requests
import json
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))
today = datetime.now(tz).strftime("%Y-%m-%d")

STOP_IDS = [6035, 7947, 12055, 1743, 3333]
ROUTE_GROUPS = {
    "藍1": ["13", "131", "14", "141"],
    "3": ["31", "32"],
    "27": ["2711", "2721"],
    "35": ["351", "352"],
    "36": ["364"]
}

def simplify_route(route_id):
    for name, ids in ROUTE_GROUPS.items():
        if route_id in ids:
            return name
    return route_id

def resolve_direction(route_id):
    if route_id in ["13", "131"]:
        return "山外"
    elif route_id in ["14", "141"]:
        return "金城"
    elif route_id in ["2711", "2721"]:
        return "沙美"
    else:
        return ""

def fetch_estimates():
    result = []
    for stop_id in STOP_IDS:
        try:
            res = requests.get(f"https://ebus.kinmen.gov.tw/xmlbus4/rest/RealTimeByStopID/{stop_id}", timeout=10)
            if res.ok:
                result.extend(res.json())
        except:
            continue
    return result

def fetch_schedule():
    try:
        res = requests.get(f"https://ebus.kinmen.gov.tw/api/schedule?date={today}", timeout=10)
        if res.ok:
            return res.json()
    except:
        pass
    return []

def main():
    est = fetch_estimates()
    sch = fetch_schedule()
    now = datetime.now(tz)

    print(f"📦 預估資料數量：{len(est)}，排班資料數量：{len(sch)}")

    est_dict = {}
    for e in est:
        key = (e.get("PlateNumb", ""), e.get("RouteId", ""))
        eta = e.get("EstimateTime", None)
        if eta is None:
            eta_text = "未發車"
        elif eta <= 60:
            eta_text = "即將進站"
        else:
            eta_text = f"{eta // 60}分"
        est_dict[key] = eta_text

    output = []
    for s in sch:
        stop_id = str(s.get("StopID", ""))
        if stop_id not in map(str, STOP_IDS):
            continue

        route_id = s.get("RouteId", "")
        plate = s.get("PlateNumb", "").strip()
        time_str = s.get("Time", "").strip()

        try:
            dep_time = datetime.strptime(time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        except:
            continue

        key = (plate, route_id)
        eta = est_dict.get(key, "未發車")

        output.append({
            "car": plate,
            "route": simplify_route(route_id),
            "eta": eta,
            "scheduled": time_str,
            "direction": resolve_direction(route_id),
            "time": time_str,
            "timestamp": dep_time.timestamp()
        })

    output.sort(key=lambda x: x["timestamp"])
    upcoming = [b for b in output if b["timestamp"] >= now.timestamp()]

    if not upcoming and len(output) >= 2:
        upcoming = output[-2:]
        upcoming.append({
            "car": "",
            "route": "",
            "eta": "",
            "scheduled": "",
            "direction": "",
            "time": "",
            "note": "末班車已離站"
        })

    for b in upcoming:
        b.pop("timestamp", None)

    if not upcoming:
        upcoming = [{
            "note": "⚠️ 無法取得公車資料，可能為深夜或 API 無回應"
        }]

    with open("docs/data/airport-bus.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
        
if __name__ == "__main__":
    main()

from datetime import datetime, timezone, timedelta
now = datetime.now(timezone(timedelta(hours=8)))
output["updated"] = now.strftime("%Y-%m-%d %H:%M:%S")

import json
print(json.dumps(output, ensure_ascii=False, indent=2))


from datetime import datetime, timezone, timedelta
now = datetime.now(timezone(timedelta(hours=8)))

output = {
    "buses": buses,
    "updated": now.strftime("%Y-%m-%d %H:%M:%S")
}

with open("docs/data/airport-bus.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("✅ airport-bus.json updated")
print(json.dumps(output, ensure_ascii=False, indent=2))
