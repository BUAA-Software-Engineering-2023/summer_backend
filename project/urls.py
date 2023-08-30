from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register('projects', ProjectViewSet)

urlpatterns = [
    path('project/deleted', get_deleted_project_view),
    path('project/restore', restore_project_view),
    path('project/duplicate', duplicate_project_view),
    path('', include(router.urls))
]
