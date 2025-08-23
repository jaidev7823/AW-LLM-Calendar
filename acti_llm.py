import sys
import requests
import datetime
from collections import defaultdict, Counter
import os.path
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from zoneinfo import ZoneInfo


# ---------------- CONFIG ----------------
ACTIVITYWATCH_URL = "http://localhost:5600/api/0/buckets/aw-watcher-window_DESKTOP-9R9SJ3O/events"
SCOPES = ["https://www.googleapis.com/auth/calendar"]
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"
# ----------------------------------------

# ---------------- GOOGLE CALENDAR ----------------
def google_calendar_service():
    if not os.path.exists("token.pickle"):
        raise RuntimeError("No token.pickle found. Run the OAuth flow once to generate it.")

    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build("calendar", "v3", credentials=creds)

def add_calendar_event(summary, description, start_time, end_time):
    service = google_calendar_service()
    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time.isoformat() },
        "end": {"dateTime": end_time.isoformat() },
    }
    created_event = service.events().insert(calendarId="primary", body=event).execute()
    print("✅ Event created:", created_event.get("htmlLink"))

# ---------------- OLLAMA ----------------
def summarize_with_ollama(report_text, model=OLLAMA_MODEL):
    payload = {
        "model": model,
        "prompt": f"Summarize this activity report into a short, natural paragraph:\n\n{report_text}\n\n"
    }
    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    summary = ""
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8")
            if '"response":"' in data:
                part = data.split('"response":"')[1].split('"')[0]
                summary += part
    return summary.strip()

# ---------------- ACTIVITYWATCH ----------------
def get_aw_events(start, end):
    params = {"start": start.isoformat(), "end": end.isoformat()}
    r = requests.get(ACTIVITYWATCH_URL, params=params)
    r.raise_for_status()
    return r.json()

# ---- Ollama summarizer ----
def summarize_with_ollama_watcher(raw_text: str) -> str:
    prompt = f"""
You are a productivity watcher. Based on the following app usage and window titles,
summarize what the user was *actually doing* in natural language.
Focus on real-world activities (e.g. "watching YouTube video", "coding project X",
"chatting with GPT about Calendar API", "browsing folders") rather than just listing apps.
If multiple things happened, list them by importance/duration.
Keep it concise but human-readable.

Data:
{raw_text}
"""
    payload = {"model": OLLAMA_MODEL, "prompt": prompt}
    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    summary = ""
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8", errors="ignore")
            if '"response":"' in data:
                part = data.split('"response":"')[1].split('"')[0]
                summary += part
    return summary.strip()


# ---- Event summarizer ----
def summarize_events(events, other_threshold=0.05):
    total_time = 0
    app_usage = Counter()
    app_titles = defaultdict(list)

    for ev in events:
        duration = ev.get("duration", 0)
        app = ev["data"].get("app", "Unknown")
        title = ev["data"].get("title", "")
        app_usage[app] += duration
        total_time += duration
        app_titles[app].append((title, duration))

    if total_time == 0:
        return "PC was off", "No activity recorded"

    # --- Aggregate small apps ---
    major_apps = {}
    other_time = 0
    for app, t in app_usage.items():
        if t / total_time >= other_threshold:
            major_apps[app] = t
        else:
            other_time += t
    if other_time > 0:
        major_apps["Other"] = other_time

    # --- Build event title (percentages) ---
    title_parts = []
    for app, t in sorted(major_apps.items(), key=lambda x: x[1], reverse=True):
        percent = (t / total_time) * 100
        app_clean = app.replace(".exe", "").capitalize()
        title_parts.append(f"{app_clean} {percent:.0f}%")
    event_title = ", ".join(title_parts)

    # --- Build raw breakdown for LLM ---
    raw_lines = []
    for app, titles in app_titles.items():
        app_total = sum(d for _, d in titles)
        percent = (app_total / total_time) * 100
        raw_lines.append(f"{app} ({percent:.1f}%):")
        for t, d in sorted(titles, key=lambda x: x[1], reverse=True)[:5]:  # top 5 titles per app
            mins = d / 60
            raw_lines.append(f"   • {t} (~{mins:.1f}m)")
    raw_text = "\n".join(raw_lines)

    # --- Summarize with Ollama (watcher style) ---
    event_description = summarize_with_ollama_watcher(raw_text)

    return event_title, event_description

# ---------------- MAIN ----------------
def process_hours(back_hours=1):
    LOCAL_TZ = ZoneInfo("Asia/Kolkata")
    now = datetime.datetime.now(LOCAL_TZ)

    for i in range(back_hours):
        # Compute the hour interval
        hour_end = now.replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=i)
        hour_start = hour_end - datetime.timedelta(hours=1)

        print(f"Processing {hour_start} → {hour_end} ...")

        events = get_aw_events(hour_start, hour_end)
        event_title, event_description = summarize_events(events)

        add_calendar_event(
            summary=event_title,
            description=event_description,
            start_time=hour_start,
            end_time=hour_end,
        )
        print(f"✅ Hour {hour_start} → {hour_end} updated.\n")

if __name__ == "__main__":
    # Default: last 1 hour
    back_hours = 1
    if len(sys.argv) > 1:
        try:
            back_hours = int(sys.argv[1])
        except ValueError:
            print("Invalid argument, using default: 1 hour")

    process_hours(back_hours)