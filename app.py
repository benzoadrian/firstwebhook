from flask import Flask, request
import requests
import json
import openai

app = Flask(__name__)

VERIFY_TOKEN = "theverifying"
WHATSAPP_TOKEN = "EAAkGYV0KptkBOyiTAF3xsvUItYQi5ZBJbVlKvDYLFDufI6DbkDWV6rJWIAUqN7lqfAfLAYcNKsi0rJkokkjmBzbO5WUGqoG4SQREbNHeWwsaHSLifYEzdYu8WbGwAJjFhrgfePRrLcCZBtxMcxZCZBY7CW4M9NlabZC8Jqe8huXrHcqITEmK0wpr5TXCeZBotQPWz6vtjmE7jaFNkaoM1qE4RP28cMuAOH83EZD"
PHONE_NUMBER_ID = "591899364010894"
OPENAI_API_KEY = "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"

# Set up OpenAI client
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

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
                                reply = generate_openai_reply(text)
                                send_whatsapp_message(sender_id, reply)

        except Exception as e:
            print("❌ Error processing webhook:", e)

        return "EVENT_RECEIVED", 200


def generate_openai_reply(user_message):
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for a medical clinic chatbot."},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content.strip()


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

