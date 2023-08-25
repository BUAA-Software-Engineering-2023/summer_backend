from django.urls import path

from .consumers import MessageConsumer

websocket_urlpatterns = [
    path('message/<str:user>', MessageConsumer.as_asgi()),
]
