import uuid
from django.db import models
from user.models import User


class Chat(models.Model):
    type_choice = [
        ('group', '群聊'),
        ('single', '私聊')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User)
    type = models.CharField(max_length=10, choices=type_choice)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def get_latest_message_time(self):
        latest_message = self.message_set.order_by('-created_time').first()
        if latest_message:
            return latest_message.created_time
        return None

class ChatMessage(models.Model):
    type_choice = [
        ('text', '文本'),
        ('image', '图片'),
        ('file', '文件')
    ]
    type = models.CharField(max_length=10, choices=type_choice)
    content = models.TextField()
    chat = models.ManyToManyField(Chat)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

