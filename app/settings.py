import os

from pydantic import BaseSettings
from yandex_tracker_client import TrackerClient
from loguru import logger
from dotenv import load_dotenv


# Подгрузить данные из .env
load_dotenv()


class Settings(BaseSettings):
    """ Общий класс настроек. (Обращение через объект класса.)"""

    DATABASE_URL = 'sqlite://app/database/database.sqlite3'
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITHM = "HS256"
    ACCESS_TOKEN_PREFIX = 'Bearer'
    ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 10080 = 1 Неделя

    APPS_MODELS = [
        'app.api_company.models',
    ]

    @property
    def tracker_client(self):
        """ Динамический аттрибут. (Объект клиента яндекс трекера.) """
        client = TrackerClient(
            token=os.getenv('TRACKER_TOKEN'),
            org_id=os.getenv('TRACKER_COMPANY_ID'),
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
