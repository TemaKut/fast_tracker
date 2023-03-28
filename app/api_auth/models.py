from tortoise import models
from tortoise import fields as f
from tortoise.contrib.pydantic import pydantic_model_creator


class Company(models.Model):
    """ Модель пользователя. """

    id = f.IntField(
        pk=True,
        unique=True,
        description='id записи в БД',
    )
    login = f.CharField(
        max_length=50,
        unique=True,
        description='Логин компании (Для авторизации)',
    )
    hashed_password = f.CharField(
        max_length=1000,
        description='Хэш пароля. (Для авторизации)',
    )
    email = f.CharField(
        max_length=50,
        unique=True,
        description='Email компании (Для резервного сброса пароля)',
    )
    period_get_tasks_sec = f.IntField(
        default=120,
        description='Время обновления задач компании из Y.T.',
    )
    incomes_queues = f.JSONField(
        default='["FINVYRUCKA"]',
        description='Список очередей с выручкой.',
    )
    expenses_queues = f.JSONField(
        default='["FINRASHODY"]',
        description='Список очередей с расходами.',
    )
    staff_salary_queues = f.JSONField(
        default='["HRPERSONAL"]',
        description='Список очередей с зарплатами сотрудников.',
    )
    receipts_queues = f.JSONField(
        default='["FINPOSTUPLENIA"]',
        description='Список очередей с поступлениями.',
    )
    payments_queues = f.JSONField(
        default='["FINPLATEZI"]',
        description='Список очередей с платежами.',
    )
    tax_queues = f.JSONField(
        default='["TAXNALOGI"]',
        description='Список очередей с налогами.',
    )
    team_queues = f.JSONField(
        default='''[
            "TEAMVA",
            "TEAMES",
            "LAYVERSTKA",
            "KOMANDAAA",
            "ENGENGINEERS",
            "DEVRAZRABOTKA",
            "BIMRAZRABOTKA",
            "ARCH",
            "HYPD"
        ]''',
        description='Список очередей с рабочими задачами сотрудников.',
    )


CompanySchema = pydantic_model_creator(Company)
