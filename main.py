from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    try:
            data = request.json
            print("Получен webhook:", json.dumps(data, indent=2))

            # Извлекаем данные из webhook
            conversation_id = data.get('data', {}).get('item', {}).get('id')
            topic = data.get('topic')

            print(f"Topic: {topic}")
            print(f"Conversation ID: {conversation_id}")

            return jsonify({"status": "ok"}), 200
        except Exception as e:
            print(f"Ошибка: {e}")
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
