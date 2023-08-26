from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from permissions import *
from .serializers import *
from .models import *
from django.db.models import Max,F


def get_latest_message_time(cls):
    latest_message = cls.chatmessage_set.order_by('-created_time').first()
    if latest_message:
        return latest_message.created_time
    return None

class ChatListView(generics.ListCreateAPIView):
    permission_classes = [IsMemberForChat]
    serializer_class = ChatSerializer

    def get_queryset(self):
        user = self.request.user
        return (Chat.objects.filter(members=user)
                .annotate(last_message_time=Max('chatmessage__created_time'))
                .order_by(F('last_message_time').desc(nulls_last=True)))
    def perform_create(self, serializer):
        name = self.request.data.get('name')
        if not name:
            members = User.objects.filter(id__in=self.request.data.get('members')).distinct().values('name')
            members = [member['name'] for member in members]
            name = ','.join(members)

        serializer.save(type='group', name=name)
