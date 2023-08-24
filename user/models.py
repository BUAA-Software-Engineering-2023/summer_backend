from django.db import models

# Create your models here.
class User(models.Model):
    email = models.EmailField('邮箱地址', unique=True)
    name = models.CharField('姓名', max_length=40)
    nickname = models.CharField('昵称', max_length=40)
    password = models.CharField('密码', max_length=200)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('活动时间', auto_now=True)
