from pydantic import BaseSettings
from yandex_tracker_client import TrackerClient
from loguru import logger


class Settings(BaseSettings):
    """ Общий класс настроек. (Обращение через объект класса.)"""
    # C какой переодичностью получать все задачи с трекера (>= 30сек!)
    PERIOG_GET_TASKS_SEC: int = 60
    # Название очереди с выручкой
    INCOMES_QUEUES: list = ['FINVYRUCKA']

    # Название очереди с расходами
    EXPENSES_QUEUES: list = ['FINRASHODY']

    # Название очереди с зарплатами персонала
    STAFF_SALARY_QUEUES: list = ['HRPERSONAL']

    # Название очереди с поступлениями
    RECEIPTS_QUEUES: list = ['FINPOSTUPLENIA']

    # Название очереди с платежами
    PAYMENTS_QUEUES: list = ['FINPLATEZI']

    # Название очереди с налогами
    TAX_QUEUES: list = ['TAXNALOGI']

    # Очереди для рабочих задач
    TEAMS_QUEUES: list = [
        'TEAMVA',
        'TEAMES',
        'LAYVERSTKA',
        'KOMANDAAA',
        'ENGENGINEERS',
        'DEVRAZRABOTKA',
        'BIMRAZRABOTKA',
        'ARCH',
        'HYPD',
    ]

    @property
    def tracker_client(self):
        """ Динамический аттрибут. (Объект клиента яндекс трекера.) """
        # TODO: Убрать в .env
        TRACKER_TOKEN = (
            'y0_AgAEA7qkDBuJAAiKegAAAADSw798XTywTZ-GRyGME90E2Nv5EljNu2A'
        )
        TRACKER_COMPANY_ID = '7012587'

        client = TrackerClient(
            token=TRACKER_TOKEN,
            org_id=TRACKER_COMPANY_ID,
        )

        return client

    @property
    def log(self):
        """ Логгер приложения. """
        logger.remove()
        logger.add(
            "logs.log",
            level='DEBUG',
            rotation="1 MB",
            format=(
                "{time:YYYY-MM-DD at HH:mm:ss} "
                "| {level} | {name} {line} | {message}"
                ),
        )

        return logger


settings = Settings()
log = settings.log
