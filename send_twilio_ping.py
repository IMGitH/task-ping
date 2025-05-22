import os
from twilio.rest import Client

sid = os.getenv('TWILIO_SID')
token = os.getenv('TWILIO_AUTH_TOKEN')
from_whatsapp = os.getenv('TWILIO_FROM')
to_whatsapp = os.getenv('TWILIO_TO')

client = Client(sid, token)
try:
    msg = client.messages.create(
        body='📢 Daily ping: keep Twilio sandbox alive',
        from_=from_whatsapp,
        to=to_whatsapp
    )
    print(f'[Twilio] Sent message SID: {msg.sid}')
except Exception as e:
    print(f'[Twilio] Failed to send message: {e}')
