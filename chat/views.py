from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from permissions import *
from .serializers import *
from .models import *
from django.db.models import Max, F, Subquery


class ChatListView(generics.ListCreateAPIView):
    """
    获取所有群组
    或
    创建单个群组
    """
    permission_classes = [IsMemberForChat]
    serializer_class = ChatSerializer

    def get_queryset(self):
        user = self.request.user
        team = self.request.query_params.get('team')
        return (Chat.objects.filter(members=user, team=team)
                .annotate(last_message_time=Max('chatmessage__created_time'))
                .order_by('-priority', F('last_message_time').desc(nulls_last=True)))
    def perform_create(self, serializer):
        name = self.request.data.get('name')
        if not name:
            # 未传递群组名称则将成员名拼接作为群组名称
            members = User.objects.filter(id__in=self.request.data.get('members')).distinct().values('name')
            members = [member['name'] for member in members]
            name = ','.join(members)

        serializer.save(type='group', name=name)

    def list(self, request, *args, **kwargs):
        ret = super().list(request, *args, **kwargs)
        try:
            # 若为管理员，每个群组添加一个id为0的用户，代表所有人，用以实现@所有人
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
    """
    获取单个群组信息
    """
    permission_classes = [IsMemberForChat]
    serializer_class = ChatSerializer

    def get_queryset(self):
        # 群组按最后一条信息发送时间排序
        user = self.request.user
        return (Chat.objects.filter(members=user, team=team)
                .annotate(last_message_time=Max('chatmessage__created_time'))
                .order_by('-priority', F('last_message_time').desc(nulls_last=True)))

@api_view(['PATCH'])
@permission_classes([IsMemberForChat])
def add_chat_member_view(request, pk):
    """
    添加群组成员
    :param request:
    :param pk: 群组id
    :return:
    """
    try:
        chat = Chat.objects.get(pk=pk)
    except Chat.DoesNotExist:
        return Response({'detail': '不存在的群组'}, status=status.HTTP_400_BAD_REQUEST)
    if chat.priority == 999:
        # 默认群聊，则拒绝变更
        return Response({'detail': '默认群聊无法变更人员'}, status=status.HTTP_400_BAD_REQUEST)
    members = request.data.get('members')
    for member in members:
        chat.members.add(member)
    return Response(None, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsMemberForChat])
def remove_chat_member_view(request, pk):
    """
    移除群组成员
    :param request:
    :param pk: 群组id
    :return:
    """
    try:
        chat = Chat.objects.get(pk=pk)
    except Chat.DoesNotExist:
        return Response({'detail': '不存在的群组'}, status=status.HTTP_400_BAD_REQUEST)
    if chat.priority == 999:
        # 默认群聊，则拒绝变更
        return Response({'detail': '默认群聊无法变更人员'}, status=status.HTTP_400_BAD_REQUEST)
    members = request.data.get('members')
    for member in members:
        chat.members.remove(member)
    if not chat.members.count():
        chat.delete()
    return Response(None, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsMemberForChat])
def get_chat_message_view(request, pk):
    """
    获取群聊的历史消息
    :param request: 请求
    :param pk: 群聊id
    :return:
    """
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


@api_view(['PATCH'])
@permission_classes([IsMemberForChat])
def read_chat_message_view(request, pk):
    """
    将群聊消息均标为已读
    :param request: 请求
    :param pk: 群聊id
    :return:
    """
    ChatMessage.objects.filter(chat=pk).update(unread=False)
    return Response(None, status=status.HTTP_200_OK)
