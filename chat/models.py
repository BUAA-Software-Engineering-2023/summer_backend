import uuid
from django.db import models

from team.models import Team
from user.models import User


class Chat(models.Model):
    type_choice = [
        ('group', '群聊'),
        ('single', '私聊')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='admin_chat')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=type_choice)
    priority = models.IntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class ChatMessage(models.Model):
    type_choice = [
        ('text', '文本'),
        ('image', '图片'),
        ('file', '文件')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=10, choices=type_choice)
    content = models.TextField()
    unread = models.BooleanField(default=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_time']
