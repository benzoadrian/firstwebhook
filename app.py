from flask import Flask, request

app = Flask(__name__)

# Set this to match the Verify Token you enter in the Meta/WhatsApp dashboard
VERIFY_TOKEN = "theverifying"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification token mismatch", 403

    elif request.method == 'POST':
        # Webhook event - could be message, status update, etc.
        data = request.json
        print("📩 Webhook Received:", data)
        return "EVENT_RECEIVED", 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
