import os
import re
import asana
from asana.rest import ApiException


class AsanaClient:
    def __init__(self):
        self.access_token = os.environ.get('ASANA_ACCESS_TOKEN')
        self.target_section_gid = os.environ.get('ASANA_TARGET_SECTION_GID')
        self.project_gid = os.environ.get('ASANA_PROJECT_GID')

        if not self.access_token:
            raise ValueError("ASANA_ACCESS_TOKEN environment variable is required")
        if not self.project_gid:
            raise ValueError("ASANA_PROJECT_GID environment variable is required")

        configuration = asana.Configuration()
        configuration.access_token = self.access_token
        self.api_client = asana.ApiClient(configuration)
        self.tasks_api = asana.TasksApi(self.api_client)
        self.sections_api = asana.SectionsApi(self.api_client)
        self.attachments_api = asana.AttachmentsApi(self.api_client)
        self.projects_api = asana.ProjectsApi(self.api_client)

    def extract_conversation_id_from_url(self, url):
        #Извлекает conversation ID из URL Intercom
        #Например: https://app.eu.intercom.com/a/inbox/grcvqyws/inbox/shared/all/conversation/4137#part_id=comment-4137-23555
        #Возвращает: 4137
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
            opts = {
                'opt_fields': 'gid,name'
            }

            tasks = self.projects_api.get_tasks_for_project(self.project_gid, opts)
            return tasks.get('data', [])
        except ApiException as e:
            print(f"Ошибка при получении задач проекта {self.project_gid}: {e}")
            return []

    def get_task_attachments(self, task_gid):
        # Получает все attachments для задачи
        try:
            opts = {
                'opt_fields': 'gid,name,resource_type,resource_subtype,url,view_url,host'
            }

            attachments = self.attachments_api.get_attachments_for_task(task_gid, opts)
            return attachments.get('data', [])
        except ApiException as e:
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

        except ApiException as e:
            print(f"Ошибка при поиске задачи: {e}")
            return None

    def move_task_to_section(self, task_gid, section_gid=None):
        # Перемещает задачу в указанную секцию
        try:
            target_section = section_gid or self.target_section_gid
            if not target_section:
                print("Не указана целевая секция для перемещения задачи")
                return False

            body = {
                'data': {
                    'task': task_gid
                }
            }

            self.sections_api.add_task_for_section(target_section, body)
            print(f"Задача {task_gid} перемещена в секцию {target_section}")
            return True

        except ApiException as e:
            print(f"Ошибка при перемещении задачи: {e}")
            return False

    def get_task_details(self, task_gid):
        # Получает детальную информацию о задаче
        try:
            opts = {
                'opt_fields': 'gid,name,notes,completed,assignee,due_on,projects'
            }

            task = self.tasks_api.get_task(task_gid, opts)
            return task

        except ApiException as e:
            print(f"Ошибка при получении деталей задачи {task_gid}: {e}")
            return None
