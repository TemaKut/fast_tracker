from tortoise.contrib.test import TestCase, initializer, finalizer
from httpx import AsyncClient
from fastapi import status

from app.main import app
from app.settings import settings
from app.api_company.models import Company

#  python -m unittest discover app/tests


class TestAuth(TestCase):
    """ Тестирование приложения авторизации. """

    def setUp(cls):
        """ Единажды выполнить эту функцию в самом начале. """
        initializer(settings.APPS_MODELS)

        cls.cl_kwargs = {'app': app, 'base_url': "http://127.0.0.1:8000"}
        cls.client = AsyncClient
        cls.GET_TOKEN_URL = '/api/v1/auth/token'
        cls.GET_INFO_COMPANY_URL = '/api/v1/auth/my_company'

    def tearDown(cls):
        finalizer()

    async def test_422_for_get_token_url_without_body(self):
        """ Проверка статуса кода 422 для эндпоинта без тела запроса. """
        async with self.client(**self.cl_kwargs) as client:
            response = await client.post(self.GET_TOKEN_URL)

            self.assertEqual(
                response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
            )

    async def test_is_company_created(self):
        """ Была ли создана компания при старте приложения. """

        companyes = await Company.all()
        print(companyes)
