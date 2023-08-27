from django.urls import path
from .views import *

urlpatterns = [
    path('designs', DesignListCreateView.as_view()),
    path('design/<str:pk>', DesignRetrieveUpdateDestroyView.as_view()),
    path('design-versions', DesignHistoryListCreateView.as_view())
]