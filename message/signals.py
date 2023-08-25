from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer


from chat.models import ChatMessage
from message.models import Message


@receiver(post_save, sender=Message)
def message_send(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    chat_group_name = f'chat_{instance.receiver.pk}'
    if created:
        if not instance.document:
            chat_message = ChatMessage.objects.get(pk=instance.chat_message.pk)
            async_to_sync(channel_layer.group_send)(
                chat_group_name,
                {
                    'type': 'chat.message',
                    'data': {
                        'chat_message': chat_message.pk,
                        'chat': chat_message.chat.pk,
                        'type': 'chat_message'
                    }
                }
            )
        else:
            async_to_sync(channel_layer.group_send)(
                chat_group_name,
                {
                    'type': 'chat.message',
                    'data': {
                        'document': instance.document.pk,
                        'type': 'document'
                    }
                }
            )