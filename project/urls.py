from django.urls import path
from .views import *

urlpatterns = [
    path('project', project_view),
    path('project/deleted', get_deleted_project_view),
    path('project/restore', restore_project_view),
    path('project/<str:id>', get_single_project_view)
]
