import os
import json
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

ANNOTATION_URL = os.getenv("ANNOTATION_URL")
SESSION_COOKIE = os.getenv("SESSION_COOKIE")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
TWILIO_TO = os.getenv("TWILIO_TO")

CACHE_FILE = "task_cache.json"

HEADERS = {
    "Cookie": SESSION_COOKIE,
    "User-Agent": "Mozilla/5.0"
}

def send_whatsapp(message: str):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_FROM,
        to=TWILIO_TO
    )

def load_cached_tasks():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return []

def save_cached_tasks(tasks):
    with open(CACHE_FILE, "w") as f:
        json.dump(tasks, f)

def get_current_tasks():
    response = requests.get(ANNOTATION_URL, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to load task page. Status: {response.status_code}")
    soup = BeautifulSoup(response.text, "html.parser")

    # TODO: Update this based on the actual HTML
    task_items = soup.select(".task-item")
    return [t.get("data-id") or t.text.strip() for t in task_items if t.text.strip()]

def check_for_new_tasks():
    try:
        current = get_current_tasks()
        previous = load_cached_tasks()
        new_tasks = list(set(current) - set(previous))
        if new_tasks:
            print(f"[+] New tasks: {new_tasks}")
            send_whatsapp("New annotation tasks:\n" + "\n".join(new_tasks))
            save_cached_tasks(current)
        else:
            print("[-] No new tasks.")
    except Exception as e:
        print(f"[!] Error: {e}")
        send_whatsapp(f"Watcher failed: {e}")

if __name__ == "__main__":
    check_for_new_tasks()
