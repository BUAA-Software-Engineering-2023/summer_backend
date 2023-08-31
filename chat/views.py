import hashlib
import os
import re

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from permissions import *
from .serializers import *
from .models import *
from django.db.models import Max, F, Subquery
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


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
        chat_type = self.request.data.get('type') or 'group'
        name = self.request.data.get('name')
        admin = self.request.user if chat_type == 'group' else None
        if not name:
            # 未传递群组名称则将成员名拼接作为群组名称
            members = User.objects.filter(id__in=self.request.data.get('members')).distinct().values('name')
            members = [member['name'] for member in members]
            name = ','.join(members)

        serializer.save(type=chat_type, name=name, admin=admin)

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
    permission_classes = [IsMemberOfChat]
    serializer_class = ChatSerializer

    def get_queryset(self):
        # 群组按最后一条信息发送时间排序
        user = self.request.user
        return (Chat.objects.filter(members=user)
                .annotate(last_message_time=Max('chatmessage__created_time'))
                .order_by('-priority', F('last_message_time').desc(nulls_last=True)))

@api_view(['PATCH'])
@permission_classes([IsAdminOfChat])
def rename_chat_view(request, pk):
    """
    重命名群组
    :param request:
    :param pk: 群组id
    :return:
    """
    try:
        chat = Chat.objects.get(pk=pk)
    except Chat.DoesNotExist:
        return Response({'detail': '不存在的群组'}, status=status.HTTP_400_BAD_REQUEST)
    chat.name = request.data.get('name') or chat.name
    chat.save()
    return Response(None, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAdminOfChat])
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
@permission_classes([IsAdminOfChat])
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
@permission_classes([IsMemberOfChat])
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
@permission_classes([IsMemberOfChat])
def read_chat_message_view(request, pk):
    """
    将群聊消息均标为已读
    :param request: 请求
    :param pk: 群聊id
    :return:
    """
    ChatMessage.objects.filter(chat=pk).update(unread=False)
    return Response(None, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsMemberOfChat])
def leave_group_view(request, pk):
    """
    普通成员退出群组，若为管理员调用，则随机选择用户作为管理员
    :param request: 请求
    :param pk: 群聊id
    :return:
    """
    try:
        chat = Chat.objects.get(pk=pk)
    except Chat.DoesNotExist:
        return Response({'detail':'不存在的群组'}, status=status.HTTP_404_NOT_FOUND)
    if chat.priority == 999:
        # 默认群聊，则拒绝变更
        return Response({'detail': '默认群聊无法退出'}, status=status.HTTP_400_BAD_REQUEST)
    if chat.type == 'single':
        return Response({'detail': '私聊无法退出'}, status=status.HTTP_400_BAD_REQUEST)
    chat.members.remove(request.user)
    if chat.admin.pk == request.user.pk:
        # 选择一位用户作为管理员
        chat.admin = chat.members.first()
    if not chat.members.count():
        # 群组不存在成员时，删除群组
        chat.delete()
    return Response(None, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAdminOfChat])
def admin_leave_group_view(request, pk):
    """
    管理员退出群聊
    :param request: 请求
    :param pk: 群聊id
    :return:
    """
    admin = request.data.get('admin')
    try:
        chat = Chat.objects.get(pk=pk)
    except Chat.DoesNotExist:
        return Response({'detail':'不存在的群组'}, status=status.HTTP_404_NOT_FOUND)
    if chat.priority == 999:
        # 默认群聊，则拒绝变更
        return Response({'detail': '默认群聊无法退出'}, status=status.HTTP_400_BAD_REQUEST)
    chat.members.remove(request.user)
    if admin:
        # 指定用户为管理员
        chat.admin = admin
    else:
        # 选择一位用户作为管理员
        chat.admin = chat.members.first()
    if not chat.members.count():
        # 群组不存在成员时，删除群组
        chat.delete()
    return Response(None, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAdminOfChat])
def delete_group_view(request, pk):
    """
    管理员删除群聊
    :param request: 请求
    :param pk: 群聊id
    :return:
    """
    admin = request.data.get('admin')
    try:
        chat = Chat.objects.get(pk=pk)
    except Chat.DoesNotExist:
        return Response({'detail': '不存在的群组'}, status=status.HTTP_404_NOT_FOUND)
    if chat.priority == 999:
        # 默认群聊，则拒绝变更
        return Response({'detail': '默认群聊无法退出'}, status=status.HTTP_400_BAD_REQUEST)
    chat.delete()
    return Response(None, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsMemberOfChat])
def forward_chat_message_view(request, pk):
    channel_layer = get_channel_layer()
    messages = request.data.get('messages')
    to = request.data.get('to')
    if not messages or not to:
        return Response({'detail': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        to_chat = Chat.objects.get(pk=to)
    except Chat.DoesNotExist:
        return Response({'detail': '不存在的群组'}, status=status.HTTP_404_NOT_FOUND)
    for message in messages:
        try:
            # 转发的消息存入数据库
            chat_message = ChatMessage.objects.get(pk=message)
            if chat_message.type == 'text':
                content = (f'<div style="font-size:10px;opacity:0.5;min-width:250px">'
                           f'<div>转发的消息</div>'
                           f'<div style="display: flex;justify-content: space-between;">'
                           f'<div>{chat_message.sender.name}</div>'
                           f'<div>{chat_message.created_time.strftime("%Y-%m-%d %H:%M:%S")}</div></div></div>'
                           f'<div style="padding-left: 1em">{chat_message.content}</div>')
            else:
                return Response({'detail': '暂不支持非文本消息的转发'}, status=status.HTTP_404_NOT_FOUND)
            chat_message = ChatMessage.objects.create(
                chat=to_chat, content=content,
                sender=request.user, type='text'
            )
            # 向群聊用户发送消息
            for member in to_chat.members.all():
                # 获取用户所在频道名
                chat_group_name = f'chat_{member.id}'
                # 序列化数据
                data = ChatMessageSerializer(instance=chat_message).data
                # 额外添加发送人姓名
                data['sender_name'] = request.user.name
                # UUID转为字符串
                for key, value in data.items():
                    data[key] = str(value)
                # 发送消息
                async_to_sync(channel_layer.group_send)(
                    chat_group_name,
                    {
                        'type': 'chat.message',
                        'data': data
                    }
                )
        except ChatMessage.DoesNotExist:
            return Response({'detail': '不存在的消息'}, status=status.HTTP_404_NOT_FOUND)
    return Response(None, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsMemberOfChat])
def forward_chat_message_together_view(request, pk):
    channel_layer = get_channel_layer()
    messages = request.data.get('messages')
    to = request.data.get('to')
    if not messages or not to:
        return Response({'detail': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        to_chat = Chat.objects.get(pk=to)
    except Chat.DoesNotExist:
        return Response({'detail': '不存在的群组'}, status=status.HTTP_404_NOT_FOUND)
    content = ''
    for message in messages:
        try:
            # 转发的消息存入数据库
            chat_message = ChatMessage.objects.get(pk=message)
            if chat_message.type == 'text':
                content += (f'<div style="font-size:10px;opacity:0.5;min-width:250px">'
                           f'<div>转发的消息</div>'
                           f'<div style="display: flex;justify-content: space-between;">'
                           f'<div>{chat_message.sender.name}</div>'
                           f'<div>{chat_message.created_time.strftime("%Y-%m-%d %H:%M:%S")}</div></div></div>'
                           f'<div style="padding-left: 1em">{chat_message.content}</div>')
            else:
                return Response({'detail': '暂不支持非文本消息的转发'}, status=status.HTTP_404_NOT_FOUND)
        except ChatMessage.DoesNotExist:
            return Response({'detail': '不存在的消息'}, status=status.HTTP_404_NOT_FOUND)

    chat_message = ChatMessage.objects.create(
        chat=to_chat, content=content,
        sender=request.user, type='text'
    )
    # 向群聊用户发送消息
    for member in to_chat.members.all():
        # 获取用户所在频道名
        chat_group_name = f'chat_{member.id}'
        # 序列化数据
        data = ChatMessageSerializer(instance=chat_message).data
        # 额外添加发送人姓名
        data['sender_name'] = request.user.name
        # UUID转为字符串
        for key, value in data.items():
            data[key] = str(value)
        # 发送消息
        async_to_sync(channel_layer.group_send)(
            chat_group_name,
            {
                'type': 'chat.message',
                'data': data
            }
        )
    return Response(None, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsMemberOfChat])
def chat_upload_file_view(request, pk):
    """
    聊天上传文件
    :param request: 请求
    :param pk: 聊天室id
    :return:
    """
    file_type = request.query_params.get('type')
    file_extension = request.query_params.get('extension')
    file = request.FILES.get('file')

    try:
        chat = Chat.objects.get(pk=pk)
    except Chat.DoesNotExist:
        return Response({'detail': '不存在的聊天'}, status=status.HTTP_404_NOT_FOUND)
    if not (file and file_type and file_extension):
        return Response({'detail': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)

    file_type = 'image' if file_type.startswith('image') else 'file'
    file = file.open('r')
    md5 = hashlib.md5(file.read()).hexdigest()
    file_name = md5 + '.' + file_extension

    os.makedirs('./media/chat/', exist_ok=True)
    if not os.path.exists(f'./media/chat/{file_name}'):
        # 存储图片
        file.seek(0)
        with open(f'./media/chat/{file_name}', 'wb') as f:
            f.write(file.read())
    # 消息存入数据库
    chat_message = ChatMessage.objects.create(
        sender=request.user,
        type=file_type,
        content=f'media/chat/{file_name}',
        chat=chat
    )
    # websocket通知用户
    channel_layer = get_channel_layer()
    # 序列化数据
    data = ChatMessageSerializer(instance=chat_message).data
    # 额外添加发送人姓名
    data['sender_name'] = request.user.name
    path = request.path
    path = re.sub(r'/api/v\d+.*', '/', path)
    data['content'] = request.build_absolute_uri(path+data['content'])
    # UUID转为字符串
    for key, value in data.items():
        data[key] = str(value)
    # 向群聊用户发送消息
    for member in chat.members.all():
        # 获取用户所在频道名
        chat_group_name = f'chat_{member.id}'
        # 发送消息
        async_to_sync(channel_layer.group_send)(
            chat_group_name,
            {
                'type': 'chat.message',
                'data': data
            }
        )
    return Response(None, status=status.HTTP_201_CREATED)