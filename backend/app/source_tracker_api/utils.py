from copy import copy
from threading import Thread
from time import sleep

from ..settings import log
from ..settings import settings


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
                log.info('Задачи получаются..')

                all_issues = settings.tracker_client.issues.get_all()
                self.all_issues = [issues for issues in all_issues]

                pause = settings.PERIOG_GET_TASKS_SEC
                log.info(f'Задачи получены. пауза {pause} сек.')

                sleep(pause)

        thread = Thread(target=get_all_issues)
        thread.start()

    async def get_list_issues(self):
        """ Получить готовый список задач из класса. """
        if not self.all_issues:
            log.critical('Выполнен запрос задач перед их получением.')
            raise ValueError('Задачи из трекера не были получены.')

        return copy(self.all_issues)


tracker_api = TrackerApi()
