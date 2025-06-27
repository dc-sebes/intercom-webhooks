from flask import Flask, request, jsonify
import os
import sys
from asana_client import AsanaClient

app = Flask(__name__)

# Инициализация Asana клиента
print("=== Инициализация Asana клиента ===")
print(f"ASANA_ACCESS_TOKEN установлен: {bool(os.environ.get('ASANA_ACCESS_TOKEN'))}")
print(f"ASANA_PROJECT_GID: {os.environ.get('ASANA_PROJECT_GID', 'НЕ УСТАНОВЛЕН')}")
print(f"ASANA_TARGET_SECTION_GID: {os.environ.get('ASANA_TARGET_SECTION_GID', 'НЕ УСТАНОВЛЕН')}")

asana_client = None
try:
    if os.environ.get('ASANA_ACCESS_TOKEN'):
        print("Создание AsanaClient...")
        asana_client = AsanaClient()
        print("✅ Asana клиент успешно инициализирован")
        print(f"Проект: {asana_client.project_gid}")
        print(f"Целевая секция: {asana_client.target_section_gid}")
    else:
        print("❌ Asana клиент не инициализирован - отсутствует ASANA_ACCESS_TOKEN")
except Exception as e:
    print(f"❌ КРИТИЧЕСКАЯ ОШИБКА при инициализации Asana клиента:")
    print(f"   Тип ошибки: {type(e).__name__}")
    print(f"   Сообщение: {e}")
    import traceback
    print(f"   Полный traceback:")
    traceback.print_exc()
    asana_client = None

print("=== Конец инициализации Asana клиента ===\n")


@app.route('/test-asana', methods=['GET'])
def test_asana():
    """
    Тестовый эндпоинт для проверки подключения к Asana
    """
    if not asana_client:
        return jsonify({
            "error": "Asana client not initialized",
            "suggestion": "Check /debug endpoint for environment variables"
        }), 500

    try:
        # Тестируем базовое подключение
        user_info = asana_client.get_user_info()

        if not user_info:
            return jsonify({
                "error": "Could not get user info from Asana API"
            }), 500

        # Тестируем получение задач из проекта
        tasks = asana_client.get_project_tasks()

        return jsonify({
            "asana_connection": "OK",
            "user_info": {
                "name": user_info.get('name'),
                "email": user_info.get('email'),
                "gid": user_info.get('gid')
            },
            "project_info": {
                "project_gid": asana_client.project_gid,
                "tasks_count": len(tasks),
                "sample_tasks": [{"gid": t["gid"], "name": t["name"]} for t in tasks[:3]]  # Показываем первые 3 задачи
            },
            "target_section_gid": asana_client.target_section_gid
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Asana API Error: {type(e).__name__}: {str(e)}",
            "suggestion": "Check your Asana token and project GID"
        }), 500


@app.route('/debug', methods=['GET'])
def debug_env():
    """
    Дебаг-эндпоинт для проверки переменных окружения
    """
    env_vars = {
        "ASANA_ACCESS_TOKEN": "***СКРЫТО***" if os.environ.get('ASANA_ACCESS_TOKEN') else "НЕ УСТАНОВЛЕН",
        "ASANA_PROJECT_GID": os.environ.get('ASANA_PROJECT_GID', 'НЕ УСТАНОВЛЕН'),
        "ASANA_TARGET_SECTION_GID": os.environ.get('ASANA_TARGET_SECTION_GID', 'НЕ УСТАНОВЛЕН'),
        "PORT": os.environ.get('PORT', 'НЕ УСТАНОВЛЕН'),
        "DEBUG": os.environ.get('DEBUG', 'НЕ УСТАНОВЛЕН'),
    }

    return jsonify({
        "environment_variables": env_vars,
        "asana_client_initialized": asana_client is not None,
        "all_env_vars_count": len(os.environ),
        "python_version": sys.version
    }), 200


@app.route('/intercom-webhook', methods=['POST'])
def handle_webhook():
    """Обработчик webhook'ов от Intercom"""
    try:
        data = request.json
        if not data:
            print("Нет JSON данных в запросе")
            return jsonify({"status": "no data"}), 400

        # Извлекаем данные из webhook'а
        conversation_id = data.get('data', {}).get('item', {}).get('id')
        topic = data.get('topic')

        print(f"Получен webhook - Topic: {topic}, Conversation ID: {conversation_id}")

        # Логируем полученные данные для отладки
        print(f"Полные данные webhook: {data}")

        if not asana_client:
            print("Asana клиент не настроен")
            return jsonify({"status": "error", "message": "Asana client not configured"}), 500

        if not conversation_id:
            print("Conversation ID не найден в webhook данных")
            return jsonify({"status": "ok", "message": "No conversation ID found"}), 200

        # Ищем задачу по conversation ID
        task = asana_client.find_task_by_conversation_id(conversation_id)

        if task:
            print(f"Найдена задача: {task['name']} (GID: {task['gid']})")

            # Перемещаем задачу в целевую секцию
            success = asana_client.move_task_to_section(task['gid'])

            if success:
                return jsonify({
                    "status": "ok",
                    "task_moved": True,
                    "task_gid": task['gid'],
                    "task_name": task['name'],
                    "conversation_id": conversation_id
                }), 200
            else:
                return jsonify({
                    "status": "ok",
                    "task_moved": False,
                    "task_found": True,
                    "task_gid": task['gid'],
                    "error": "Не удалось переместить задачу"
                }), 200
        else:
            print(f"Задача с Conversation ID {conversation_id} не найдена")
            return jsonify({
                "status": "ok",
                "task_found": False,
                "conversation_id": conversation_id,
                "message": f"Task with conversation ID {conversation_id} not found"
            }), 200

    except Exception as e:
        print(f"Ошибка при обработке webhook: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Проверка здоровья сервиса
    """
    status = {
        "status": "healthy",
        "asana_client_configured": asana_client is not None,
        "environment_check": {
            "ASANA_ACCESS_TOKEN": bool(os.environ.get('ASANA_ACCESS_TOKEN')),
            "ASANA_PROJECT_GID": bool(os.environ.get('ASANA_PROJECT_GID')),
            "ASANA_TARGET_SECTION_GID": bool(os.environ.get('ASANA_TARGET_SECTION_GID')),
        }
    }

    if asana_client:
        status.update({
            "project_gid": asana_client.project_gid,
            "target_section_configured": asana_client.target_section_gid is not None
        })

    return jsonify(status), 200


@app.route('/test-search/<conversation_id>', methods=['GET'])
def test_search(conversation_id):
    """
    Тестовый эндпоинт для поиска задачи по conversation ID
    """
    if not asana_client:
        return jsonify({"error": "Asana client not configured"}), 400

    task = asana_client.find_task_by_conversation_id(conversation_id)

    if task:
        return jsonify({
            "found": True,
            "task": task
        }), 200
    else:
        return jsonify({
            "found": False,
            "conversation_id": conversation_id
        }), 404


@app.route('/', methods=['GET', 'POST'])
def root():
    """Корневой эндпоинт"""
    if request.method == 'GET':
        return jsonify({
            "message": "Intercom Webhook Handler",
            "endpoints": {
                "webhook": "/intercom-webhook",
                "health": "/health",
                "debug": "/debug",
                "test_asana": "/test-asana",
                "test_search": "/test-search/<conversation_id>"
            }
        }), 200
    elif request.method == 'POST':
        return handle_webhook()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    print(f"Запуск сервера на порту {port}")
    print(f"Debug режим: {debug}")
    print(f"Asana клиент инициализирован: {asana_client is not None}")
    app.run(host='0.0.0.0', port=port, debug=debug)
