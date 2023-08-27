from django.urls import path

from .consumers import DocumentConsumer

websocket_urlpatterns = [
    path('document/<str:user>', DocumentConsumer.as_asgi()),
]
