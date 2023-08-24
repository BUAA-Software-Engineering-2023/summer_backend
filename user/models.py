from django.db import models

# Create your models here.
class User(models.Model):
    email = models.EmailField('邮箱地址', unique=True)
    name = models.CharField('姓名', max_length=40)
    nickname = models.CharField('昵称', max_length=40)
    password = models.CharField('密码', max_length=200)
