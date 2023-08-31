from rest_framework import serializers
from .models import *
from user.serializers import UserSerializer


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    class Meta:
        model = ChatMessage
        fields = '__all__'

    def get_sender_name(self, chat_message):
        return chat_message.sender.name

class ChatSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all())
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    admin = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    class Meta:
        model = Chat
        fields = '__all__'
        extra_kwargs = {
            'name': {'required': False},
            'type': {'read_only': True},
        }
        depth = 2
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['members'] = UserSerializer(instance.members, many=True).data
        return ret
    def get_last_message(self, chat):
        last_message = chat.chatmessage_set.all().first()
        if not last_message:
            return None
        return ChatMessageSerializer(instance=last_message).data

    def get_unread_count(self, chat):
        return chat.chatmessage_set.filter(unread=True).count()