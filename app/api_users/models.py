from tortoise import models
from tortoise import fields as f


class User(models.Model):
    """ Модель пользователя. """

    id = f.IntField(pk=True)
    username = f.CharField(max_length=50, unique=True)
    hashed_password = f.CharField(max_length=1000)
    tracker_token = f.CharField(max_length=1000)
    tracker_company_id = f.IntField()
