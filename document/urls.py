from django.urls import path, include
from rest_framework.routers import DefaultRouter

from document.views import DocumentViewSet, authorize_share_view, read_document_view, get_histories_view, \
    restore_history_view, migrate_documents_view, save_document_view, authorization_check_view, \
    synchronize_document_view

router = DefaultRouter(trailing_slash=False)
router.register('documents', DocumentViewSet)

urlpatterns = [
    path('documents/authorize', authorize_share_view),
    path('documents/read', read_document_view),
    path('documents/history', get_histories_view),
    path('documents/restore', restore_history_view),
    path('documents/migrate', migrate_documents_view),
    path('documents/save', save_document_view),
    path('documents/synchronize/<str:pk>', synchronize_document_view),
    path('documents/check', authorization_check_view),
    path('', include(router.urls))
]
