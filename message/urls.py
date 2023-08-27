from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter(trailing_slash=False)
router.register('messages', MessageViewSet)

urlpatterns = [
    path('messages/delete', delete_messages_view),
    path('messages/read', read_messages_view),
    path('', include(router.urls))
]
