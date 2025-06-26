from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/intercom-webhook', methods=['POST'])
def handle_webhook():
    try:
        data = request.json
        print("Получен webhook:", json.dumps(data, indent=2))

        conversation_id = data.get('data', {}).get('item', {}).get('id')
        print(f"Conversation ID: {conversation_id}")

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
