from flask import Flask, request
import requests
import json
import openai

app = Flask(__name__)

# Set your tokens here
VERIFY_TOKEN = "theverifying"
WHATSAPP_TOKEN = "EAAkGYV0KptkBOx8w4lSPFbYZCbAn1WZBT4FKxRiGPoM4ZBe1yleBUQZBsEa82WEqwSkcac7hrfdfEPJ6UZC4YWB2WNedfSkcv8CuSLgWbXOPiOzDhRnQvRI0qu62ZAf0lDhdR0ksX7eYsXxjS1Q0Ti5cI1AbcdVurxQCEFb5sw8wl36G7ej5kDRuXjOe5ctDKsRrcAobXpBROMkshRXwBZAnxGVy1IZCeNm5EesZD"
PHONE_NUMBER_ID = "591899364010894"

# OpenAI key
openai.api_key = "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"

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
                                reply = get_openai_response(text)
                                send_whatsapp_message(sender_id, reply)

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


def get_openai_response(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful and friendly medical assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("❌ OpenAI error:", e)
        return "Sorry, I'm having trouble answering that right now."


if __name__ == '__main__':
    app.run(debug=True, port=5000)
