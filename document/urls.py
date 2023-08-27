from django.urls import path, include
from rest_framework.routers import DefaultRouter

from document.views import DocumentViewSet, authorize_share_view, read_document_view, get_histories_view, \
    restore_history_view

router = DefaultRouter(trailing_slash=False)
router.register('documents', DocumentViewSet)

urlpatterns = [
    path('documents/authorize/<str:pk>', authorize_share_view),
    path('documents/read', read_document_view),
    path('documents/history', get_histories_view),
    path('documents/restore', restore_history_view),
    path('', include(router.urls))
]