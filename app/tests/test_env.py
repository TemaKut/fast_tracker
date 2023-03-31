import os
from unittest import TestCase

from dotenv import load_dotenv
from yandex_tracker_client import TrackerClient
from yandex_tracker_client.exceptions import Forbidden

# Подгрузить переменные окружения
load_dotenv()


class TestEnv(TestCase):
    """ Тестирование .env """

    def test_env_variables(self):
        """ Проверка наличия переменных окружения. """
        self.assertIsNotNone(os.getenv('SECRET_KEY'))
        self.assertIsNotNone(os.getenv('TRACKER_TOKEN'))
        self.assertIsNotNone(os.getenv('TRACKER_COMPANY_ID'))
        self.assertIsNotNone(os.getenv('COMPANY_LOGIN'))
        self.assertIsNotNone(os.getenv('COMPANY_PASSWORD'))
        self.assertIsNotNone(os.getenv('COMPANY_EMAIL'))

    def test_tracker_connection(self):
        """ Смог ли подключиться клиент трекера к организации. """
        token = os.getenv('TRACKER_TOKEN')
        org_id = os.getenv('TRACKER_COMPANY_ID')

        client = TrackerClient(token=token, org_id=org_id)

        try:
            client.issues.get_all()

        except Exception:
            self.fail("(Токен | id)!!!")

    def test_tracker_connection_fail(self):
        """ Смог ли подключиться клиент трекера к организации (Fail). """
        token = os.getenv('TRACKER_TOKEN') + 'wsd2131'
        org_id = os.getenv('TRACKER_COMPANY_ID') + '14232141332'

        client = TrackerClient(token=token, org_id=org_id)

        self.assertRaises(Forbidden, client.issues.get_all)
