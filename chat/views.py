from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from permissions import *
from .serializers import *
from .models import *
from django.db.models import Max, F, Subquery


class ChatListView(generics.ListCreateAPIView):
    permission_classes = [IsMemberForChat]
    serializer_class = ChatSerializer

    def get_queryset(self):
        user = self.request.user
        return (Chat.objects.filter(members=user)
                .annotate(last_message_time=Max('chatmessage__created_time'))
                .order_by('-priority', F('last_message_time').desc(nulls_last=True)))
    def perform_create(self, serializer):
        name = self.request.data.get('name')
        if not name:
            members = User.objects.filter(id__in=self.request.data.get('members')).distinct().values('name')
            members = [member['name'] for member in members]
            name = ','.join(members)

        serializer.save(type='group', name=name)

    def list(self, request, *args, **kwargs):
        ret = super().list(request, *args, **kwargs)
        try:
            TeamMember.objects.get(
                team=self.request.query_params.get('team'),
                member=self.request.user,
                role__in=['creator', 'admin']
            )
            for chat in ret.data:
                chat['members'].append({
                    'id': 0,
                    'name': '所有人',
                    'username': 'all'
                })
                return ret
        except TeamMember.DoesNotExist:
            return ret


class ChatRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsMemberForChat]
    serializer_class = ChatSerializer

    def get_queryset(self):
        user = self.request.user
        return (Chat.objects.filter(members=user)
                .annotate(last_message_time=Max('chatmessage__created_time'))
                .order_by('-priority', F('last_message_time').desc(nulls_last=True)))

@api_view(['GET'])
@permission_classes([IsMemberForChat])
def chat_message_view(request, pk):
    id = request.query_params.get('id')
    count = int(request.query_params.get('count', 100))
    search = request.query_params.get('search')

    if search:
        sub = (ChatMessage.objects.filter(chat=pk)
            .filter(content__contains=search)
            .aggregate(max_created_time=Max('created_time')))

        queryset = (ChatMessage.objects.filter(chat=pk)
                    .filter(content__contains=search)
                    .filter(created_time__lte=sub['max_created_time']))

    elif id:
        queryset = (ChatMessage.objects.filter(chat=pk)
        .filter(created_time__lt=Subquery(
            ChatMessage.objects.filter(pk=id).values('created_time')
        )))[:count]
    else:
        queryset = ChatMessage.objects.filter(chat=pk)[:count]
    serializer = ChatMessageSerializer(instance=queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
