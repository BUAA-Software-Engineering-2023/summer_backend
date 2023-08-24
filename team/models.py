from django.db import models
import uuid
from models import SoftDeleteModel
from user.models import User


class Team(SoftDeleteModel):
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


class TeamInvite(models.Model):
    class InvitationStatus(models.TextChoices):
        SEND = 'send', '已发送'
        ACCEPT = 'accept', '已同意'
        REJECT = 'reject', '已拒绝'
        CANCEL = 'cancel', '已取消'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name='邀请团队')
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='被邀请人')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    status = models.CharField('邀请状态', choices=InvitationStatus.choices,
                              max_length=10, default=InvitationStatus.SEND)