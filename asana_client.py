import os
import re
import requests

class AsanaClient:
    def __init__(self):
        print("=== Начало инициализации AsanaClient ===")

        # Получаем переменные окружения
        self.access_token = os.environ.get('ASANA_ACCESS_TOKEN')
        self.target_section_gid = os.environ.get('ASANA_TARGET_SECTION_GID')
        self.project_gid = os.environ.get('ASANA_PROJECT_GID')

        print(f"access_token получен: {bool(self.access_token)}")
        print(f"target_section_gid: {self.target_section_gid}")
        print(f"project_gid: {self.project_gid}")

        # Проверяем обязательные переменные
        if not self.access_token:
            print("ОШИБКА: ASANA_ACCESS_TOKEN не установлен")
            raise ValueError("ASANA_ACCESS_TOKEN environment variable is required")
        if not self.project_gid:
            print("ОШИБКА: ASANA_PROJECT_GID не установлен")
            raise ValueError("ASANA_PROJECT_GID environment variable is required")

        print("Переменные окружения проверены успешно")

        # Настройка HTTP-клиента для Asana API
        self.base_url = "https://app.asana.com/api/1.0"
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        # Проверяем подключение
        try:
            print("Проверка подключения к Asana API...")
            response = requests.get(f"{self.base_url}/users/me", headers=self.headers, timeout=10)

            if response.status_code == 200:
                user_data = response.json()['data']
                print(f"✅ Подключение к Asana успешно! Пользователь: {user_data.get('name', 'Unknown')}")
            else:
                print(f"❌ Ошибка подключения к Asana: {response.status_code}")
                print(f"Response: {response.text}")
                raise Exception(f"Asana API error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка сетевого запроса к Asana: {e}")
            raise e
        except Exception as e:
            print(f"❌ Ошибка при проверке подключения к Asana: {e}")
            raise e

        print("=== AsanaClient инициализирован успешно ===")

    def _make_request(self, method, endpoint, data=None, params=None):
        #Выполняет HTTP-запрос к Asana API
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
                print(f"❌ Asana API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error in Asana request: {e}")
            return None
        except Exception as e:
            print(f"❌ Error in Asana request: {e}")
            return None

    def extract_conversation_id_from_url(self, url):
        #Извлекает conversation ID из URL Intercom
        if not url:
            return None

        # Ищем паттерн /conversation/NUMBER
        match = re.search(r'/conversation/(\d+)', url)
        if match:
            return match.group(1)

        return None

    def get_project_tasks(self):
        #Получает все задачи из указанного проекта
        try:
            print(f"Получение задач из проекта {self.project_gid}")

            params = {
                'project': self.project_gid,
                'opt_fields': 'gid,name',
                'limit': 100  # Ограничиваем количество для безопасности
            }

            result = self._make_request('GET', '/tasks', params=params)

            if result and 'data' in result:
                tasks = result['data']
                print(f"Получено {len(tasks)} задач")
                return tasks
            else:
                print("Не удалось получить задачи из проекта")
                return []

        except Exception as e:
            print(f"Ошибка при получении задач проекта {self.project_gid}: {e}")
            return []

    def get_task_attachments(self, task_gid):
        #Получает все attachments для задачи
        try:
            params = {
                'parent': task_gid,
                'opt_fields': 'gid,name,resource_type,resource_subtype,url,view_url,host'
            }

            result = self._make_request('GET', '/attachments', params=params)

            if result and 'data' in result:
                return result['data']
            else:
                return []

        except Exception as e:
            print(f"Ошибка при получении attachments для задачи {task_gid}: {e}")
            return []

    def find_task_by_conversation_id(self, conversation_id):
        #Находит задачу по conversation ID среди attachments всех задач проекта
        try:
            print(f"Поиск задачи с conversation ID: {conversation_id}")

            # Получаем все задачи проекта
            tasks = self.get_project_tasks()
            print(f"Найдено {len(tasks)} задач в проекте {self.project_gid}")

            for task in tasks:
                task_gid = task['gid']
                task_name = task.get('name', 'Без названия')

                # Получаем attachments для задачи
                attachments = self.get_task_attachments(task_gid)

                for attachment in attachments:
                    # Проверяем view_url и url
                    for url_field in ['view_url', 'url']:
                        url = attachment.get(url_field)
                        if url:
                            extracted_id = self.extract_conversation_id_from_url(url)
                            if extracted_id == str(conversation_id):
                                print(f"Найдена задача: {task_name} (GID: {task_gid})")
                                print(f"Conversation ID найден в {url_field}: {url}")
                                return {
                                    'gid': task_gid,
                                    'name': task_name,
                                    'attachment_gid': attachment['gid'],
                                    'conversation_url': url
                                }

            print(f"Задача с conversation ID {conversation_id} не найдена")
            return None

        except Exception as e:
            print(f"Ошибка при поиске задачи: {e}")
            return None

    def move_task_to_section(self, task_gid, section_gid=None):
        #Перемещает задачу в указанную секцию
        try:
            target_section = section_gid or self.target_section_gid
            if not target_section:
                print("Не указана целевая секция для перемещения задачи")
                return False

            # Добавляем задачу в секцию через Asana API
            data = {
                'data': {
                    'task': task_gid
                }
            }

            result = self._make_request('POST', f'/sections/{target_section}/addTask', data=data)

            if result:
                print(f"Задача {task_gid} перемещена в секцию {target_section}")
                return True
            else:
                print(f"Не удалось переместить задачу {task_gid} в секцию {target_section}")
                return False

        except Exception as e:
            print(f"Ошибка при перемещении задачи: {e}")
            return False

    def get_task_details(self, task_gid):
        #Получает детальную информацию о задаче
        try:
            params = {
                'opt_fields': 'gid,name,notes,completed,assignee,due_on,projects'
            }

            result = self._make_request('GET', f'/tasks/{task_gid}', params=params)

            if result and 'data' in result:
                return result['data']
            else:
                return None

        except Exception as e:
            print(f"Ошибка при получении деталей задачи {task_gid}: {e}")
            return None

    def get_user_info(self):
        #Получает информацию о текущем пользователе
        try:
            result = self._make_request('GET', '/users/me')
            if result and 'data' in result:
                return result['data']
            return None
        except Exception as e:
            print(f"Ошибка при получении информации о пользователе: {e}")
            return None
