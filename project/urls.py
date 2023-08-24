from django.urls import path
from .views import *

urlpatterns = [
    path('project', project_view, name='project'),
    path('project/<str:id>', get_single_project_view, name='project')
]