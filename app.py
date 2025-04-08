import openai
from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

VERIFY_TOKEN = "theverifying"
WHATSAPP_TOKEN = "EAAkGYV0KptkBOwJk2fsHkNuD5TN46XQmCgyr4nzGWZC782dAhlP2uXqPimWjBDVR7fUK6rFitZCtdtbZALdHmudA9tnAtbPKnsZBJ5iypk5Vpq1Cf2AMRlp5G4dOAyn19DiUCv5ZA2Qz8H2fbqopjApDUeGWXAZCx5OxodsWmL21qhuzZCOoEBILVGZC2nJlXQNcOs5BhD7Lvn7QOhT29zbLYB9QgVqZCZAsEHqxAZD"
PHONE_NUMBER_ID = "591899364010894"

openai.api_key = os.environ.get("OPENAI_API_KEY")


# Test OpenAI key on start
try:
    openai.Model.list()
    print("✅ OpenAI API key is working!")
except Exception as e:
    print("❌ OpenAI key error:", e)

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
            if 'entry' in data:
                for entry in data['entry']:
                    changes = entry.get('changes', [])
                    for change in changes:
                        value = change.get('value', {})
                        messages = value.get('messages', [])

                        for message in messages:
                            sender_id = message['from']
                            text = message['text']['body'] if message.get('text') else None

                            print(f"📨 Message from {sender_id}: {text}")

                            if text:
                                # Use ChatCompletion instead of Completion
                                response = openai.ChatCompletion.create(
                                    model="gpt-3.5-turbo",
                                    messages=[
                                        {"role": "system", "content": "You are a helpful medical assistant for Maison Abeille, a clinic in Paris: https://www.maisonabeille-chirurgie-dermatologique.com/, give clients links for consultations from here: https://www.doctolib.fr/cabinet-medical/paris/maison-abeille-chirurgie-dermatologique-medecine-dermo-esthetique"},
                                        {"role": "user", "content": text}
                                    ],
                                    max_tokens=150,
                                    temperature=0.7
                                )

                                reply_text = response['choices'][0]['message']['content'].strip()
                                send_whatsapp_message(sender_id, reply_text)

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
