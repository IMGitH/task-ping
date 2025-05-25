import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

sid = os.getenv('TWILIO_SID')
token = os.getenv('TWILIO_AUTH_TOKEN')
from_whatsapp = os.getenv('TWILIO_FROM')  # Format: whatsapp:+14155238886
to_whatsapp = os.getenv('TWILIO_TO')      # Format: whatsapp:+9725xxxxxxx

client = Client(sid, token)

try:
    msg = client.messages.create(
        from_=from_whatsapp,
        to=to_whatsapp,
        messaging_product="whatsapp",
        template={
            "name": "daily_ping_alert",
            "language": { "code": "en" },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        { "type": "text", "text": "keep Twilio sandbox alive" }
                    ]
                }
            ]
        }
    )
    print(f'[Twilio] Sent template message SID: {msg.sid}')
except Exception as e:
    print(f'[Twilio] Failed to send template message: {e}')
