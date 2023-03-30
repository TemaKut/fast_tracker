import os

from unittest import TestCase

from dotenv import load_dotenv

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
