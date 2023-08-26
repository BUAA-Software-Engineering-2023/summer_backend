from django.urls import path
from .views import *

urlpatterns = [
    path('register', UserCreateView.as_view()),
    path('users', UserListView.as_view()),
    path('login', login_password_view)
]