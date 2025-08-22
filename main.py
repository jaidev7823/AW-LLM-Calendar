import requests
import datetime
from collections import Counter

# --- CONFIG ---
ACTIVITYWATCH_URL = "http://localhost:5600/api/0/buckets/aw-watcher-window_DESKTOP-9R9SJ3O/events"
# --------------

def get_aw_events(start, end):
    """Fetch events from ActivityWatch within time window"""
    params = {"start": start.isoformat(), "end": end.isoformat()}
    r = requests.get(ACTIVITYWATCH_URL, params=params)
    r.raise_for_status()
    return r.json()

def summarize_events(events):
    """Group events by app and calculate percentage usage"""
    total_time = 0
    usage = Counter()

    for ev in events:
        duration = ev.get("duration", 0)
        app = ev["data"].get("app", "Unknown")
        usage[app] += duration
        total_time += duration

    if total_time == 0:
        return "No activity recorded."

    summary_lines = []
    for app, t in usage.most_common():
        percent = (t / total_time) * 100
        summary_lines.append(f"{app}: {percent:.1f}%")

    return "\n".join(summary_lines)

def main():
    now = datetime.datetime.utcnow()
    one_hour_ago = now - datetime.timedelta(hours=1)

    events = get_aw_events(one_hour_ago, now)
    summary = summarize_events(events)

    print("Summary of last hour:")
    print(summary)

if __name__ == "__main__":
    main()
