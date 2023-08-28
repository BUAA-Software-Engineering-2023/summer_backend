from django.urls import path

from .consumers import ChatConsumer

websocket_urlpatterns = [
    path('chat/<str:user>', ChatConsumer.as_asgi()),
]