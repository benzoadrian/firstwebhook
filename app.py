from flask import Flask, request
import requests
import json

app = Flask(__name__)

VERIFY_TOKEN = "theverifying"
WHATSAPP_TOKEN = "EAAkGYV0KptkBOx8w4lSPFbYZCbAn1WZBT4FKxRiGPoM4ZBe1yleBUQZBsEa82WEqwSkcac7hrfdfEPJ6UZC4YWB2WNedfSkcv8CuSLgWbXOPiOzDhRnQvRI0qu62ZAf0lDhdR0ksX7eYsXxjS1Q0Ti5cI1AbcdVurxQCEFb5sw8wl36G7ej5kDRuXjOe5ctDKsRrcAobXpBROMkshRXwBZAnxGVy1IZCeNm5EesZD"
PHONE_NUMBER_ID = "591899364010894"  # e.g., 591899364010894

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification token mismatch", 403

    elif request.method == 'POST':
        data = request.get_json()
        print("📩 Webhook Received:", json.dumps(data, indent=2))

        try:
            # Check if it's a message and not a delivery/read status
            if 'entry' in data:
                for entry in data['entry']:
                    changes = entry.get('changes', [])
                    for change in changes:
                        value = change.get('value', {})
                        messages = value.get('messages', [])

                        for message in messages:
                            sender_id = message['from']  # WhatsApp ID of the sender (phone number)
                            text = message['text']['body'] if message.get('text') else None

                            print(f"📨 Message from {sender_id}: {text}")

                            # Send hardcoded reply
                            send_whatsapp_message(sender_id, "Hey! This is an automated test reply from shaken noy stirred")

        except Exception as e:
            print("❌ Error processing webhook:", e)

        return "EVENT_RECEIVED", 200


def send_whatsapp_message(to_number, message_text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print(f"📤 Sent message to {to_number}. Status code: {response.status_code}")
    print(response.json())


if __name__ == '__main__':
    app.run(debug=True, port=5000)
