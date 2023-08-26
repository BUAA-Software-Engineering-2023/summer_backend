from django.urls import path
from .views import *

urlpatterns = [
    path('chats', ChatListView.as_view())
]