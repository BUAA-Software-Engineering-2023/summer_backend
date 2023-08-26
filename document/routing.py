from django.urls import path

from .consumers import TipTapConsumer

websocket_urlpatterns = [
    path('textcollab/<str:user>', TipTapConsumer.as_asgi()),
]