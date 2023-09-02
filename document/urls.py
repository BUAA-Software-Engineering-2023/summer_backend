from django.urls import path, include
from rest_framework.routers import DefaultRouter

from document.views import *

router = DefaultRouter(trailing_slash=False)
router.register('documents', DocumentViewSet)
router.register('document-folders', DocumentFolderViewSet)

urlpatterns = [
    path('documents/authorize', authorize_share_view),
    path('documents/deauthorize', deauthorize_share_view),
    path('documents/read', read_document_view),
    path('documents/history', get_histories_view),
    path('documents/restore', restore_history_view),
    path('documents/migrate', migrate_documents_view),
    path('documents/save', save_document_view),
    path('documents/synchronize/<str:pk>', synchronize_document_view),
    path('documents/check', authorization_check_view),
    path('docments/tree', get_document_tree_view),
    path('documents/template', get_document_template_view),
    path('documents/mention', document_mention_view),
    path('', include(router.urls))
]
