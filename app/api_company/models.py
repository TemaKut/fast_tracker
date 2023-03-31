from tortoise import models
from tortoise.validators import MinLengthValidator, MinValueValidator
from tortoise import fields as f
from tortoise.contrib.pydantic import pydantic_model_creator
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        validators=[MinLengthValidator(2)],
    )
    password = f.CharField(
        max_length=1000,
        description='Хэш пароля. (Для авторизации)',
        validators=[MinLengthValidator(6)],
    )
    email = f.CharField(
        max_length=50,
        description='Email компании (Для резервного сброса пароля)',
    )
    period_get_tasks_sec = f.IntField(
        default=120,
        description='Время обновления задач компании из Y.T.',
        validators=[MinValueValidator(29)],
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

    def verify_password(self, password: str) -> bool:
        """ Верифицировать пароль. """

        return pwd_context.verify(password, self.password)

    async def save(self, *args, **kwargs) -> None:
        """ Переопределение метода save. """
        self.password = pwd_context.hash(self.password)

        await super().save(*args, **kwargs)


# Описание схем pydantic
CompanyAllSchema = pydantic_model_creator(Company, name='Полная схема')
CompanyForTokenSchema = pydantic_model_creator(
    Company,
    include=('login', 'password'),
    name='Определённые поля для получения токена'
)
