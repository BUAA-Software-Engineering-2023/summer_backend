from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from user.models import User


class MessageConsumer(JsonWebsocketConsumer):
    # websocket建立连接时执行方法
    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user']
        try:
            self.user = User.objects.get(pk=self.user_id)
        except User.DoesNotExist:
            self.close()
            return

        self.chat_group_name = f'message_{self.user_id}'
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

    # 从频道组接收到消息后执行方法
    def chat_message(self, event):
        # 通过websocket发送消息到客户端
        data = event['data']
        if data['type'] == 'chat_message':
            self.send_json({
                'type': 'chat_message',
                'chat_message': str(data.get('chat_message')),
                'chat': str(data.get('chat')),
            })
        else:
            self.send_json({
                'type': 'document',
                'document': str(data['document']),
            })
