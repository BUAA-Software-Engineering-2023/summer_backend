from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    chat = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'
        extra_kwargs = {"chat_message": {"required": False}, "document": {"required": False}}

    def get_chat(self, message):
        if message.chat_message:
            return message.chat_message.chat.id
        return None

    def get_team(self, message):
        if message.chat_message:
            return message.chat_message.chat.team.id
        return None
