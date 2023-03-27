from copy import copy, deepcopy
from threading import Thread
from time import sleep
from datetime import datetime as dt

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
        self.hour_salary_for_personal: dict | None = None
        self._work_hours_per_month = {
            "01": 136,
            "02": 144,
            "03": 176,
            "04": 160,
            "05": 160,
            "06": 168,
            "07": 168,
            "08": 184,
            "09": 168,
            "10": 176,
            "11": 168,
            "12": 168,
        }

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
                self.__put_hour_salary_for_personal(data)

                # Пауза перед получением актуального списка задач
                pause = settings.PERIOG_GET_TASKS_SEC

                log.info(f'Задачи получены. пауза {pause} сек.')
                sleep(pause)

        # Запустить получение задач в отдельном потоке
        thread = Thread(target=get_all_issues)
        thread.start()

    async def get_personal_salaryes(self) -> dict:
        """ Вернуть словать с ежемесячными зарплатами сотрудников. """
        if not self.hour_salary_for_personal:
            log.critical('Не удалось получить зарплаты сотрудников')
            raise ValueError('Не удалось получить зарплаты сотрудников')

        return deepcopy(self.hour_salary_for_personal)

    def __put_hour_salary_for_personal(self, issues: list) -> None:
        """ Из всех задач вычислить часовую зарплату для персонала. """
        if not issues:
            log.critical('Для вычисления часовой ставки нет задач.')

            return None

        pre_hour_salary_for_personal = {}

        for issue in issues:

            if (
                issue.queue.key in settings.STAFF_SALARY_QUEUES
                and issue.assignee
                and issue.end
                and issue.summaEtapa
            ):
                if issue.end.split("-")[0] != str(dt.now().year):
                    continue

                end_month = issue.end.split("-")[1]
                summa = issue.summaEtapa
                staff = issue.assignee.display
                hour_salary = summa / self._work_hours_per_month[end_month]
                hour_salary = round(hour_salary, 4)

                if m := pre_hour_salary_for_personal.get(end_month):

                    m[staff] = hour_salary

                else:
                    pre_hour_salary_for_personal[end_month] = {
                        staff: hour_salary
                    }

        self.hour_salary_for_personal = pre_hour_salary_for_personal

    async def get_list_issues(self):
        """ Получить готовый список задач из класса. """
        if not self.all_issues:
            log.critical('Выполнен запрос задач перед их получением.')
            raise ValueError('Задачи из трекера не были получены.')

        return copy(self.all_issues)


# Объект класса взаимодействия с трекером и задачами
# Следует обращаться к методам класса TrackerApi только через этот объект.
tracker_api = TrackerApi()
