# Data Annotation Watcher

This app monitors dataannotation.tech for available projects and sends you WhatsApp notifications using Twilio.

## Features

- Authenticates using your logged-in session cookie
- Extracts tasks from the embedded JSON on the page
- Two modes:
  - mode=1 – Detect and alert about new tasks (cached)
  - mode=2 – Just send a list of current available tasks
- Designed for GitHub Actions + manual use

## How It Works

1. Scrapes your annotation dashboard
2. Extracts task data from the data-props JSON inside the DOM
3. Notifies you via WhatsApp (using Twilio Sandbox)
4. Caches previous tasks locally (task_cache.json) to detect new ones

## Environment Variables

Can be loaded via .env (locally) or GitHub Actions Secrets.

| Variable            | Description                                               |
|---------------------|-----------------------------------------------------------|
| ANNOTATION_URL      | Task page URL (e.g., https://app.dataannotation.tech/workers/projects) |
| SESSION_COOKIE      | Your full session cookie (copied from the Application tab in DevTools under `https://www.dataannotation.tech`; must include HttpOnly cookies that are not visible via JavaScript) |
| TWILIO_SID          | Your Twilio Account SID (from https://www.twilio.com/console) |
| TWILIO_AUTH_TOKEN   | Your Twilio Auth Token |
| TWILIO_FROM         | whatsapp:+14155238886 (Twilio sandbox sender) |
| TWILIO_TO           | Your verified WhatsApp number with whatsapp:+ prefix |

## How to Use Locally

### 1. Install dependencies

pip install -r requirements.txt

### 2. Create a .env file

ANNOTATION_URL=https://www.dataannotation.tech/tasks  
SESSION_COOKIE=_session_id=abc123; auth_token=xyz456  
TWILIO_SID=ACxxxxxxxxxxxxxxxxxxxxxxxx  
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxx  
TWILIO_FROM=whatsapp:+14155238886  
TWILIO_TO=whatsapp:+<your_verified_number>

Get your session cookie from DevTools > Application > Cookies (must include HttpOnly cookies).

### 3. Run manually

- **Detect new tasks and notify:**
python watcher.py 1
- **Just send current task list:**
python watcher.py 2

## GitHub Actions Workflow

Supports manual runs and cross-run task caching.

### Notes

- GitHub runner is stateless — use actions/cache to persist task history
- You can refresh your cookie any time by logging in again and copying updated values from DevTools
- This workflow is already configured to run automatically every 15 minutes during daytime using a `cron` schedule



## Twilio WhatsApp Setup

1. Go to https://www.twilio.com/console/sms/whatsapp/learn  
2. Send the sandbox join code from your WhatsApp to: +1 415 523 8886  
3. Set:  
   TWILIO_FROM=whatsapp:+14155238886  
   TWILIO_TO=whatsapp:+<your_verified_number>

You must use the same WhatsApp number you joined with.

## Notes

- GitHub runner is stateless — use actions/cache to persist task history  
- You can refresh your cookie any time by logging in again and copying updated values from DevTools
- To keep the Twilio Sandbox session alive, a scheduled GitHub Actions workflow sends a daily WhatsApp ping at 08:00 Israel time:
  - Requires you to manually send a WhatsApp message to the sandbox number at least once every 24h to keep the window open
  - Workflow file: .github/workflows/keep-twilio-sandbox-alive.yml
  - Script file: .github/scripts/send_twilio_ping.py

