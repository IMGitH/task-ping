import os
import json
import html
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
from dotenv import load_dotenv


class AnnotationWatcher:
    def __init__(self):
        load_dotenv()  # Optional: for local dev

        self.annotation_url = os.getenv("ANNOTATION_URL")
        self.session_cookie = os.getenv("SESSION_COOKIE")

        self.twilio_sid = os.getenv("TWILIO_SID")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from = os.getenv("TWILIO_FROM")
        self.twilio_to = os.getenv("TWILIO_TO")

        self.cache_file = "task_cache.json"

        self.headers = {
            "Cookie": self.session_cookie,
            "User-Agent": "Mozilla/5.0"
        }

    def send_whatsapp(self, message: str):
        client = Client(self.twilio_sid, self.twilio_token)
        client.messages.create(body=message, from_=self.twilio_from, to=self.twilio_to)

    def get_current_tasks(self):
        response = requests.get(self.annotation_url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Failed to load task page. Status: {response.status_code}")
        if "Login" in response.text:
            raise Exception("You're not logged in. SESSION_COOKIE is invalid or expired.")
        soup = BeautifulSoup(response.text, "html.parser")

        root_div = soup.find("div", id="workers/WorkerProjectsTable-hybrid-root")
        if not root_div:
            raise Exception("Could not find task container in page.")

        raw_json = root_div.get("data-props")
        if not raw_json:
            raise Exception("No data-props attribute found.")

        # Decode HTML-escaped JSON string
        decoded_json = html.unescape(raw_json)
        data = json.loads(decoded_json)

        # Extract the list of projects
        projects = data.get("dashboardMerchTargeting", {}).get("projects", [])
        task_names = [proj["name"] for proj in projects if proj.get("availableTasksFor", "0") != "0"]

        return task_names


    def load_cached_tasks(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                return json.load(f)
        return []

    def save_cached_tasks(self, tasks):
        with open(self.cache_file, "w") as f:
            json.dump(tasks, f)

    def check_for_new_tasks(self):
        current_tasks = self.get_current_tasks()
        print("[*] Current tasks:")
        for t in current_tasks:
            print(f"- {t}")
        previous_tasks = self.load_cached_tasks()
        new_tasks = list(set(current_tasks) - set(previous_tasks))
        if new_tasks:
            print("[+] New tasks detected:")
            for t in new_tasks:
                print(f"\t+ {t}")
            msg = (
                "📌 *New annotation tasks available!*\n\n"
                + "\n".join(
                    f"▫️ *{task.split(':')[0]}:* {task.split(':', 1)[1]}" if ':' in task else f"▫️ {task}"
                    for task in new_tasks
                )
                + "\n\n🔗 *Go to tasks:* https://www.dataannotation.tech/worker"
            )
            self.send_whatsapp(msg)
            self.save_cached_tasks(current_tasks)
        else:
            print("[-] No new tasks.")


    def send_current_tasks(self):
        current_tasks = self.get_current_tasks()

        if current_tasks:
            message = (
                "📋 *Current tasks:*\n\n"
                + "\n".join(
                    f"▫️ *{task.split(':')[0]}:* {task.split(':', 1)[1]}" if ':' in task else f"▫️ {task}"
                    for task in current_tasks
                )
            )
        else:
            message = "✅ *No current tasks found.*"

        print(message)
        self.send_whatsapp(message)


if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "1"

    watcher = AnnotationWatcher()

    if mode == "1":
        watcher.check_for_new_tasks()
    elif mode == "2":
        watcher.send_current_tasks()
    else:
        print(f"[!] Unknown mode '{mode}', use '1' or '2'.")
