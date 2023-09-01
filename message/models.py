import uuid

from django.db import models

from user.models import User

from chat.models import ChatMessage

from document.models import Document


# Create your models here.
class Message(models.Model):
    id = models.UUIDField('id', primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField('消息内容', default='')
    is_read = models.BooleanField('是否已读', default=False)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('活动时间', auto_now=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='接收者', related_name='receiver',
                                 blank=True, default=0)
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, verbose_name='消息', related_name='message',
                                     blank=True, null=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, verbose_name='项目文件', related_name='file',
                                 blank=True, null=True)

    class Meta:
        ordering = ['-create_time']
