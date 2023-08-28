from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

team_invite_router = DefaultRouter(trailing_slash=False)

urlpatterns = [
    path('teams', TeamListCreateView.as_view()),
    path('team/<str:pk>', TeamRetrieveUpdateDestroyView.as_view()),
    path('team/<str:pk>/admin/add', add_admin_view),
    path('team/<str:pk>/admin/remove', remove_admin_view),
    path('team/<str:pk>/member/remove', remove_member_view),
    path('team-invites', TeamInviteListCreateView.as_view()),
    path('team-invite/resolve/<str:pk>', resolve_invite_view)
]