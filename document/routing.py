from django.urls import path

from .consumers import DocumentConsumer

websocket_urlpatterns = [
    path('ws/document/<str:user>', DocumentConsumer.as_asgi()),
]
