from rest_framework import serializers
from .models import *
from user.serializers import UserSerializer

class ChatSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    class Meta:
        model = Chat
        fields = '__all__'
        extra_kwargs = {
            'name': {'required': False},
            'type': {'read_only': True}
        }
        depth = 2
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['members'] = UserSerializer(instance.members, many=True).data
        return ret

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'

