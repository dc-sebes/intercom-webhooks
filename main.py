from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

@app.route('/intercom-webhook', methods=['POST'])
def handle_webhook():
    try:
        print("Headers:", dict(request.headers))
        print("Raw data:", request.get_data())

        data = request.json
        if not data:
            print("Нет JSON данных в запросе")
            return jsonify({"status": "no data"}), 400

        print("Получен webhook:", json.dumps(data, indent=2))

        conversation_id = data.get('data', {}).get('item', {}).get('id')
        topic = data.get('topic')

        print(f"Topic: {topic}")
        print(f"Conversation ID: {conversation_id}")

        # Здесь добавить логику работы с Asana API

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "Intercom Webhook Handler"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
