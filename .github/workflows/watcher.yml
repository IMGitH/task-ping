import os
import json
import html
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from twilio.rest import Client
from dotenv import load_dotenv


class AnnotationWatcher:
    def __init__(self):
        load_dotenv()

        self.annotation_url = os.getenv("ANNOTATION_URL")
        self.session_cookie = os.getenv("SESSION_COOKIE")
        self.twilio_sid = os.getenv("TWILIO_SID")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from = os.getenv("TWILIO_FROM")  # Format: whatsapp:+14155238886
        self.twilio_to = os.getenv("TWILIO_TO")      # Format: whatsapp:+9725xxxxxxx
        self.cache_file = "task_cache.json"

        self.headers = {
            "Cookie": self.session_cookie,
            "User-Agent": "Mozilla/5.0"
        }
        self.twilio_balance_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Balance.json"

    def send_whatsapp_template(self, task_name: str, task_url: str):
        print(f"[+] Sending WhatsApp template for task: {task_name}")
        client = Client(self.twilio_sid, self.twilio_token)
        client.messages.create(
            from_=self.twilio_from,
            to=self.twilio_to,
            messaging_product="whatsapp",
            template={
                "name": "task_update_alert",
                "language": { "code": "en" },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            { "type": "text", "text": task_name },
                            { "type": "text", "text": task_url }
                        ]
                    }
                ]
            }
        )

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

        decoded_json = html.unescape(raw_json)
        data = json.loads(decoded_json)

        projects = data.get("dashboardMerchTargeting", {}).get("projects", [])
        return [(proj["id"], proj["name"]) for proj in projects if proj.get("availableTasksFor", "0") != "0"]

    def load_cached_tasks(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                return json.load(f)
        return []

    def save_cached_tasks(self, tasks):
        with open(self.cache_file, "w") as f:
            json.dump(tasks, f)

    def check_for_updates_in_tasks(self):
        current_tasks = self.get_current_tasks()
        print("[*] Current tasks:")
        for _, name in current_tasks:
            print(f"- {name}")

        previous_tasks = self.load_cached_tasks()

        prev_ids = {t[0] for t in previous_tasks}
        curr_ids = {t[0] for t in current_tasks}

        new_tasks = [t for t in current_tasks if t[0] not in prev_ids]
        removed_tasks = [t for t in previous_tasks if t[0] not in curr_ids]

        if removed_tasks:
            print("[INFO] Removed tasks:")
            for _, name in removed_tasks:
                print(f"\t- {name}")
        if new_tasks:
            print("\n[+] New tasks detected:")
            for _, name in new_tasks:
                print(f"\t+ {name}")

        if new_tasks:
            for _, name in new_tasks:
                self.send_whatsapp_template(name, self.annotation_url)
            self.save_cached_tasks(current_tasks)
        else:
            print("[-] No new tasks to notify.")

    def log_twilio_balance(self):
        try:
            response = requests.get(
                self.twilio_balance_url,
                auth=HTTPBasicAuth(self.twilio_sid, self.twilio_token)
            )
            if response.status_code == 200:
                data = response.json()
                print(f"\n[Twilio] Balance: {data['balance']} {data['currency']}")
            else:
                print(f"\n[Twilio] Could not fetch balance. HTTP {response.status_code}")
        except Exception as e:
            print(f"\n[Twilio] Error fetching balance: {e}")


if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "1"
    watcher = AnnotationWatcher()

    if mode == "1":
        watcher.check_for_updates_in_tasks()
        watcher.log_twilio_balance()
    else:
        print(f"[!] Unknown mode '{mode}', use '1'.")
