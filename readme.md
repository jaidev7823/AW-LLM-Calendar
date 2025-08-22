# AW-LLM-Calendar: Automated Time-Logging with a Local LLM

**AW-LLM-Calendar** bridges your digital life with your schedule by connecting **ActivityWatch**, **Google Calendar**, and a **Local LLM** (via [Ollama](https://ollama.ai/)). It automatically fetches your tracked computer activity, uses a local language model to generate a human-readable summary of what you were doing, and creates detailed, hourly events in your Google Calendar.

Keep your productivity logs private and automated—no cloud AI services needed.

---
<img src="/assets/Before integrating tool.png" width="70" />
---

## ✨ Features

-   **⏱️ Automated Activity Tracking**: Pulls application usage and window title data directly from your [ActivityWatch](https://activitywatch.net/) instance.
-   **🧠 Intelligent Summarization**: Uses a local LLM (default: [Mistral](https://ollama.ai/library/mistral)) to transform raw data into a meaningful summary of your activities.
-   **📅 Smart Calendar Events**: Automatically creates hourly Google Calendar events with:
    -   **Title**: A clean, at-a-glance breakdown of app usage (e.g., `Chrome 60%, VS Code 30%, Other 10%`).
    -   **Description**: The LLM-generated summary of what you were *actually* doing (e.g., "Primarily researched Python's asyncio library on Chrome, worked on the 'async-feature' branch in VS Code, and briefly checked emails.").
-   **✅ Fully Local & Private**: Your activity data is processed on your machine and never sent to an external AI service.

---

## 🚀 Setup

### 1. Prerequisites

-   [Python 3.10+](https://www.python.org/downloads/)
-   [ActivityWatch](https://activitywatch.net/downloads/) installed and running.
-   [Ollama](https://ollama.ai/download) installed and running.
-   The `mistral` LLM pulled via Ollama.
    ```bash
    ollama pull mistral
    ```

### 2. Install Python Dependencies

Install the required Python libraries using pip:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib requests
```

### 3. Google Calendar API Authentication

You need to authorize the script to access your Google Calendar.

1.  **Enable the API**: Go to the [Google Cloud Console](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com) and enable the **Google Calendar API** for your project.
2.  **Create Credentials**: Go to the [Credentials page](https://console.cloud.google.com/apis/credentials) and create an **OAuth 2.0 Client ID** for a **Desktop application**.
3.  **Download Credentials**: Download the JSON file and rename it to `credentials.json` in your project directory.
4.  **Authenticate**: Run the `calender.py` script **once** to authenticate.
    ```bash
    python calender.py
    ```
    Your web browser will open, asking you to log in and grant permission. Upon success, a `token.pickle` file will be created. This file stores your login session for future runs.

---

## ⚡ Usage

Run the `acti_llm.py` script to fetch the previous hour's activity, summarize it, and log it to your Google Calendar.

```bash
python acti_llm.py
```

**Example Output:**

```
✅ Event created: https://calendar.google.com/event?eid=...
```

**Example Calendar Entry:**

> **Title:** `Chrome 70%, Code 20%, Other 10%`
>
> **Description:**
>
> `Spent most of the hour browsing Python documentation on Chrome, working on the main script in Visual Studio Code, and briefly checking messages on Slack.`

You can set this up as a cron job or a scheduled task to run automatically every hour.

---

## 🛠 Roadmap

-   [*] **Hourly Summaries**: Roll up hourly logs into insightful daily or weekly reports with productivity scoring.
-   [*] **Update on Google Calender**: summarize and update on google calender.
-   [ ] **Automation**: Automatically updating google calender on hourly basis
-   [ ] **Daily summarization**: based on calender data summarize daily.
-   [ ] **Goal Integration**: Compare planned tasks (e.g., from a to-do list) with actual tracked activity.
-   [ ] **Productivity Tracker**: Track how much task was done and how is left how time got wasted how much work is done
-   [ ] **Smarter Categorization**: Automatically classify activities as "Work," "Leisure," or "Neutral."

---

## 📜 License

This project is licensed under the MIT *License. See the [LICENSE](LICENSE) file for details.

---

## 🙌 Credits

-   **[ActivityWatch](https://activitywatch.net/)** for the comprehensive, local-first time-tracking engine.
-   **[Ollama](https://ollama.ai/)** for making it simple to run powerful LLMs locally.
-   The **[Google Calendar API](https://developers.google.com/calendar)** for easy calendar integration.