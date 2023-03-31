import json

from tortoise.contrib.test import TestCase, initializer, finalizer
from httpx import AsyncClient
from fastapi import status

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

    async def test_raise_get_token_url_with_false_login(self):
        """ Проверка ошибки при получении токена с неправильным логином. """
        data = {'login': 'falseLogin', 'password': 'falsepassword'}

        async with self.client(**self.cl_kwargs) as client:
            response = await client.post(self.GET_TOKEN_URL, json=data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_raise_get_token_url_with_false_password(self):
        """ Проверка ошибки при получении токена с неправильным паролем. """
        await Company.create(
            login="Hyperion_login",
            password="Hyperion_pass",
            email="tema.kutuzzzov@yandex.ru",
        )

        data = {'login': 'Hyperion_login', 'password': 'falsepassword'}

        async with self.client(**self.cl_kwargs) as client:
            response = await client.post(self.GET_TOKEN_URL, json=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    async def test_get_token_url_with_correct_data(self):
        """ Проверка ошибки при получении токена с правильными данными. """
        await Company.create(
            login="Hyperion_login",
            password="Hyperion_pass",
            email="tema.kutuzzzov@yandex.ru",
        )

        data = {'login': 'Hyperion_login', 'password': 'Hyperion_pass'}

        async with self.client(**self.cl_kwargs) as client:
            response = await client.post(self.GET_TOKEN_URL, json=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = json.loads(response.text)

        self.assertEqual(
            response_data['token_type'],
            sett.ACCESS_TOKEN_PREFIX,
        )
