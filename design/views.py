from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from permissions import *
from .serializers import *
from .models import *

class DesignListCreateView(generics.ListCreateAPIView):
    serializer_class = DesignSerializer
    permission_classes = [IsMemberForDesign]

    def get_queryset(self):
        project = self.request.data.get('project') or self.request.query_params.get('project')
        return Design.objects.filter(project=project)

    def perform_create(self, serializer):
        design = serializer.save()
        DesignHistory.objects.create(design=design)

class DesignRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Design.objects.all()
    serializer_class = DesignWithDataSerializer
    permission_classes = [IsMemberForDesign]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

class DesignHistoryListCreateView(generics.ListCreateAPIView):
    serializer_class = DesignHistorySerializer
    permission_classes = [IsMemberForDesign]

    def get_queryset(self):
        design = self.request.query_params.get('design')
        return DesignHistory.objects.filter(design=design)
