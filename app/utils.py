from copy import copy
from threading import Thread
from time import sleep

from .settings import log
from .settings import settings


class TrackerApi:
    """
    Основные методы работы с API Яндекс Трекера.
    (Обращаться через объект ниже).
    """

    def __init__(self):
        """ Инициализация класса. """
        self.all_issues: list | None = None

    def get_all_issues_from_tracker(self):
        """ Получить все задачи из трекера (В отдельном потоке). """
        def get_all_issues():
            """ Получить все задачи из трекера. """
            while True:
                all_issues = settings.tracker_client.issues.get_all()

                # Из paginated list создать список
                data = []

                for issue in all_issues:

                    # Если резолюция задачи "wontFix" -> игнорировать.
                    try:
                        resolution = issue.resolution.key
                    except Exception:
                        resolution = None

                    if resolution != 'wontFix':
                        data.append(issue)

                self.all_issues = data

                # Пауза перед получением актуального списка задач
                pause = settings.PERIOG_GET_TASKS_SEC

                log.info(f'Задачи получены. пауза {pause} сек.')
                sleep(pause)

        # Запустить получение задач в отдельном потоке
        thread = Thread(target=get_all_issues)
        thread.start()

    async def get_list_issues(self):
        """ Получить готовый список задач из класса. """
        if not self.all_issues:
            log.critical('Выполнен запрос задач перед их получением.')
            raise ValueError('Задачи из трекера не были получены.')

        return copy(self.all_issues)


# Объект класса взаимодействия с трекером и задачами
# Следует обращаться к методам класса TrackerApi только через этот объект.
tracker_api = TrackerApi()
