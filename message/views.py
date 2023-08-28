from .serializers import MessageSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from message.models import Message


# Create your views here.
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(receiver=user)

    def perform_update(self, serializer):
        serializer.save(is_read=True)


@api_view(['DELETE'])
def delete_messages_view(request):
    user = request.user
    try:
        Message.objects.filter(is_read=True, receiver=user).delete()
        return Response({'detail': '所有已读消息删除成功'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': '消息删除失败,' + e.args[0]}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def read_messages_view(request):
    user = request.user
    try:
        messages = Message.objects.filter(receiver=user)
        for message in messages:
            message.is_read = True
            message.save()
        return Response({'detail': '消息全部已读'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': '消息已读失败,' + e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
