from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from user.models import User
from chat.models import Chat,ChatMessage
from django.db.models import Q


class ChatConsumer(JsonWebsocketConsumer):
    # websocket建立连接时执行方法
    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user']
        try:
            self.user = User.objects.get(pk=self.user_id)
        except User.DoesNotExist:
            self.close()
            return

        self.chat_group_name = f'chat_{self.user_id}'
        # 每个用户建立一个频道组
        async_to_sync(self.channel_layer.group_add)(
            self.chat_group_name,
            self.channel_name
        )

        # 接受所有websocket请求
        self.accept()


    # websocket断开时执行方法
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data:
            try:
                self.receive_json(self.decode_json(text_data), **kwargs)
            except:
                self.send_json({
                    'success': False,
                    'detail': '仅支持JSON格式文本'
                })
        else:
            raise ValueError("No text section for incoming WebSocket frame!")

    # 从websocket接收到消息时执行函数
    def receive_json(self, content, **kwargs):
        chat = content.get('chat')
        if not chat:
            receiver = content.get('receiver')
            try:
                receiver = User.objects.get(pk=receiver)
            except User.DoesNotExist:
                self.send_json({
                    'success': False,
                    'detail': '无对应用户'
                })
                return
            try:
                chat = Chat.objects.filter(Q(members=self.user)).get(
                    Q(members=receiver)&Q(type='single')
                )
            except Chat.DoesNotExist:
                chat = Chat.objects.create(
                    name=f'{self.user.name}-{receiver.name}',
                    type='single'
                )
                chat.members.add(self.user)
                chat.members.add(receiver)
        else:
            try:
                chat = Chat.objects.get(pk=chat)
            except:
                self.send_json({
                    'success': False,
                    'detail': '无对应聊天'
                })
                return
        content['chat'] = str(chat.id)

        # 消息存储到数据库
        ChatMessage.objects.create(
            type=content.get('type'), content=content.get('content'),
            chat=chat, sender=self.user
        )

        # 发送消息至用户
        members = chat.members.filter(~Q(pk=self.user.pk))
        for member in members:
            # 发送消息到频道组，频道组调用chat_message方法
            async_to_sync(self.channel_layer.group_send)(
                f'chat_{member.id}',
                {'type': 'chat.message', 'data': content}
            )

        self.send_json({
            'success': True
        })


    # 从频道组接收到消息后执行方法
    def chat_message(self, event):
        data= event['data']

        # 通过websocket发送消息到客户端
        self.send_json({
            'content': data.get('content'),
            'type': data.get('type'),
            'chat': data.get('chat')
        })
