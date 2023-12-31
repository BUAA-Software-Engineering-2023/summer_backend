from django.db import models
from models import SoftDeleteModel


class User(SoftDeleteModel):
    email = models.EmailField('邮箱地址', unique=True)
    name = models.CharField('姓名', max_length=40)
    username = models.CharField('用户名', max_length=20, unique=True)
    password = models.CharField('密码', max_length=200)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('活动时间', auto_now=True)
