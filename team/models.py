from django.db import models
import uuid
from user.models import User


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('团队名称', max_length=100)
    members = models.ManyToManyField(User, through='TeamMember', verbose_name='团队成员')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('活动时间', auto_now=True)

class TeamMember(models.Model):
    class Role(models.TextChoices):
        CREATOR = 'creator', '团队创建者'
        ADMIN = 'admin', '团队管理员'
        MEMBER = 'member', '普通成员'

    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name='团队')
    member = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='成员')
    role = models.CharField('角色', choices=Role.choices, default=Role.MEMBER, max_length=10)
