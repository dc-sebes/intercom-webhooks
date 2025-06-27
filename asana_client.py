import os
import re
import asana


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

        # Инициализация клиента Asana
        try:
            print("Инициализация Asana клиента...")
            self.client = asana.Client.access_token(self.access_token)
            print("Asana клиент создан успешно")

            # Проверяем подключение
            print("Проверка подключения к Asana...")
            me = self.client.users.me()
            print(f"Подключение успешно! Пользователь: {me.get('name', 'Unknown')}")

        except Exception as e:
            print(f"ОШИБКА при инициализации Asana клиента: {type(e).__name__}: {e}")
            raise e

        print("=== AsanaClient инициализирован успешно ===")

    def get_project_tasks(self):
        # Получает все задачи из указанного проекта
        try:
            tasks = self.client.tasks.find_all({
                'project': self.project_gid,
                'opt_fields': 'gid,name'
            })
            return list(tasks)
        except Exception as e:
            print(f"Ошибка при получении задач проекта {self.project_gid}: {e}")
            return []

    def get_task_attachments(self, task_gid):
        # Получает все attachments для задачи
        try:
            attachments = self.client.attachments.find_by_task(task_gid, {
                'opt_fields': 'gid,name,resource_type,resource_subtype,url,view_url,host'
            })
            return list(attachments)
        except Exception as e:
            print(f"Ошибка при получении attachments для задачи {task_gid}: {e}")
            return []

    def find_task_by_conversation_id(self, conversation_id):
        # Находит задачу по conversation ID среди attachments всех задач проекта
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
        # Перемещает задачу в указанную секцию
        try:
            target_section = section_gid or self.target_section_gid
            if not target_section:
                print("Не указана целевая секция для перемещения задачи")
                return False

            # Добавляем задачу в секцию
            self.client.sections.add_task(target_section, {
                'task': task_gid
            })

            print(f"Задача {task_gid} перемещена в секцию {target_section}")
            return True

        except Exception as e:
            print(f"Ошибка при перемещении задачи: {e}")
            return False

    def get_task_details(self, task_gid):
        # Получает детальную информацию о задаче
        try:
            task = self.client.tasks.find_by_id(task_gid, {
                'opt_fields': 'gid,name,notes,completed,assignee,due_on,projects'
            })
            return task

        except Exception as e:
            print(f"Ошибка при получении деталей задачи {task_gid}: {e}")
            return None
