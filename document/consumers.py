import json
import logging
import time

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from document.models import Document, DocumentHistory
from message.models import Message
from user.models import User


class DocumentConsumer(JsonWebsocketConsumer):
    # websocket建立连接时执行方法
    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user']
        try:
            self.user = User.objects.get(pk=self.user_id)
        except User.DoesNotExist:
            self.close()
            return

        self.chat_group_name = f'document_{self.user_id}'
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
            except json.JSONDecodeError:
                self.send_json({
                    'success': False,
                    'detail': '仅支持JSON格式文本'
                })
            except Exception as e:
                logging.warning(f'websocket未知错误：{e}')
                self.send_json({
                    'success': False,
                    'detail': '未知错误'
                })
        else:
            raise ValueError("No text section for incoming WebSocket frame!")

    # 从websocket接收到消息时执行函数
    def receive_json(self, content, **kwargs):
        if content.get('type') == 'mentioned':
            receiver = content.get('receiver')
            document = content.get('document')
            try:
                receiver = User.objects.get(pk=receiver)
            except User.DoesNotExist:
                self.send_json({
                    'success': False,
                    'detail': '无对应用户'
                })
                return
            sender_name = self.user.name
            document = Document.objects.get(pk=document)
            document_name = document.title
            Message.objects.create(
                receiver=receiver,
                content=f'{sender_name}在文件{document_name}中@了你‘',
                document=document
            )

            self.send_json({
                'success': True,
                'detail': '已@用户'
            })
        elif content.get('type') == 'request_save':
            document_id = content.get('document')
            # get the latest data in DocumentHistory
            try:
                document_history = DocumentHistory.objects.filter(
                    document=document_id,
                    is_deleted=False
                ).latest('update_time')
                if (time.time() - document_history.update_time.timestamp()) < 600:
                    self.send_json({
                        'success': False,
                        'detail': '文件已被其他人保存'
                    })
                    return
            except DocumentHistory.DoesNotExist:
                self.send_json({
                    'success': False,
                    'detail': '无对应文件'
                })
                return
            self.send_json({
                'success': True,
                'content': '连接成功，可以保存文档'
            })
        elif content.get('type') == 'do_save':
            document_id = content.get('document')
            try:
                document = Document.objects.get(pk=document_id)
            except Document.DoesNotExist:
                self.send_json({
                    'success': False,
                    'detail': '无对应文件'
                })
                return
            DocumentHistory.objects.create(
                document=document,
                content=content.get('content')
            )
            self.send_json({
                'success': True,
                'detail': '保存成功'
            })
        else:
            self.send_json({
                'success': False,
                'detail': '无对应操作'
            })
