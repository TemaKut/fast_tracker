from tortoise.contrib.test import TestCase, initializer, finalizer
from httpx import AsyncClient

from app.main import app
from app.api_company.models import Company
from app.settings import settings as sett

#  python -m unittest discover app/tests


class TestAuth(TestCase):
    """ Тестирование приложения авторизации. """

    def setUp(cls):
        """ Единажды выполнить эту функцию в самом начале. """
        initializer(sett.APPS_MODELS)

        cls.cl_kwargs = {'app': app, 'base_url': "http://127.0.0.1:8000"}
        cls.client = AsyncClient

    def tearDown(cls):
        finalizer()

    # async def test_is_company_created_with_startup(self):
    #     """ Создаётся ли компания при старте приложения. """
    #     print(dir(app))
