from django.urls import path
from .views import *

urlpatterns = [
    path('chats', ChatListView.as_view()),
    path('chat/<str:pk>', ChatRetrieveView.as_view()),
    path('chat/<str:pk>/rename', rename_chat_view),
    path('chat/<str:pk>/add-member', add_chat_member_view),
    path('chat/<str:pk>/remove-member', remove_chat_member_view),
    path('chat/<str:pk>/message', get_chat_message_view),
    path('chat/<str:pk>/read', read_chat_message_view)
]