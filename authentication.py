import jwt
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from user.models import User
from django.conf import settings

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            user_id = payload['id']
            user = User.objects.get(pk=user_id, is_deleted=False)
            return user, token
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token已过期')
        except (jwt.DecodeError, User.DoesNotExist):
            raise exceptions.AuthenticationFailed('无效的Token')
