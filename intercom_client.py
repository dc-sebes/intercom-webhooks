import os
import requests
import json


class IntercomClient:
    def __init__(self):
        print("=== Начало инициализации IntercomClient ===")

        # Получаем переменные окружения
        self.access_token = os.environ.get('INTERCOM_ACCESS_TOKEN')

        print(f"access_token получен: {bool(self.access_token)}")

        # Проверяем обязательные переменные
        if not self.access_token:
            print("ОШИБКА: INTERCOM_ACCESS_TOKEN не установлен")
            raise ValueError("INTERCOM_ACCESS_TOKEN environment variable is required")

        print("Переменные окружения проверены успешно")

        # Настройка HTTP-клиента для Intercom API
        self.base_url = "https://api.intercom.io"
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        # Проверяем подключение
        try:
            print("Проверка подключения к Intercom API...")
            response = requests.get(f"{self.base_url}/me", headers=self.headers, timeout=10)

            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Подключение к Intercom успешно! Пользователь: {user_data.get('name', 'Unknown')}")
                print(f"Тип пользователя: {user_data.get('type', 'Unknown')}")
                print(f"Email: {user_data.get('email', 'Unknown')}")
            else:
                print(f"❌ Ошибка подключения к Intercom: {response.status_code}")
                print(f"Response: {response.text}")
                raise Exception(f"Intercom API error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка сетевого запроса к Intercom: {e}")
            raise e
        except Exception as e:
            print(f"❌ Ошибка при проверке подключения к Intercom: {e}")
            raise e

        print("=== IntercomClient инициализирован успешно ===")

    def intercom_me(self):
        try:
            me = self._make_request('GET', 'me')
        except Exception as e:
            print(f"❌ Ошибка при получении данных пользователя из Intercom: {e}")
            raise e
        return me

    def _make_request(self, method, endpoint, data=None, params=None):
        #Выполняет HTTP-запрос к Intercom API
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data, params=params, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"❌ Intercom API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error in Intercom request: {e}")
            return None
        except Exception as e:
            print(f"❌ Error in Intercom request: {e}")
            return None

    def get_conversation(self, conversation_id):
        try:
            response = self._make_request('GET', f'conversations/{conversation_id}')
            if response:
                return response
            else:
                print(f"❌ Failed to retrieve conversation with ID {conversation_id}")
                return None
        except Exception as e:
            print(f"❌ Error in get_conversation: {e}")
            return None

    def get_conversation_attributes(self, conversation_id, attribute_name):
        try:
            conversation = self.get_conversation(conversation_id)

            if not conversation:
                print(f"❌ Conversation with ID {conversation_id} not found")
                return None

            custom_attributes = conversation.get('custom_attributes', {})

            if custom_attributes:
                return custom_attributes.get(attribute_name)
            else:
                print(f"❌ Failed to retrieve custom_attributes for {conversation_id}")
                return None
        except Exception as e:
            print(f"❌ Error in get_conversation_attributes: {e}")
            return None

    def update_conversation_custom_attributes(self, conversation_id, custom_attributes):
        try:

            data = {
                "custom_attributes": custom_attributes
            }

            response = self._make_request('PUT', f'conversations/{conversation_id}', data=data)

            if response:
                return response
            else:
                print(f"❌ Failed to update conversation attributes for ID {conversation_id}")
                return None
        except Exception as e:
            print(f"❌ Error in update_conversation_attributes: {e}")
            return None

    def set_conversation_asana_link(self, conversation_id, asana_task_url):
        try:
            existing_link = self.get_conversation_attributes(conversation_id, 'asana_task_url')

            if existing_link == asana_task_url:
                print(f"✅ Asana link already set for conversation, existing_link = {existing_link}")
                return True

            custom_attributes = {
                'asana_task_url': asana_task_url
            }

            response = self.update_conversation_custom_attributes(conversation_id, custom_attributes)

            if response:
                print(f"✅ Asana link set for conversation {conversation_id}")
                return True
            else:
                print(f"❌ Failed to set Asana link for conversation {conversation_id}")
                return False
        except Exception as e:
            print(f"❌ Error in set_conversation_asana_link: {e}")
            return False
