from django.urls import path
from .views import *

urlpatterns = [
    path('chats', ChatListView.as_view()),
    path('chat/<str:pk>', ChatRetrieveView.as_view()),
    path('chat/<str:pk>/message', chat_message_view),
]