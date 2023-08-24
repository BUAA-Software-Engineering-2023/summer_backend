import uuid

from django.db import models


# Create your models here.
class Project(models.Model):
    id = models.UUIDField('id', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('项目名称', max_length=100)
    describe = models.TextField('项目描述', default='')
    is_deleted = models.BooleanField('状态', default=0)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('活动时间', auto_now=True)
