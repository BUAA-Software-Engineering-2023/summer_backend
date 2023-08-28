from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework import status, generics, filters

from utils.token import make_token
from .serializers import *
from .models import *


@api_view(['POST'])
@authentication_classes([])
def login_password_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'detail': '请完整填写用户名和密码'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        if check_password(password, user.password):
            token = make_token({'id': user.id})
            return Response({'token': token, 'id': user.id}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': '无效的用户名或密码'}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({'detail': '无效的用户名或密码'}, status=status.HTTP_401_UNAUTHORIZED)


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = []


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = []
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'username', 'name']
    class CustomLimitOffsetPagination(LimitOffsetPagination):
        default_limit = 20
    pagination_class = CustomLimitOffsetPagination
