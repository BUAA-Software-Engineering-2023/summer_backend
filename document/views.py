from django.shortcuts import render

# Create your views here.
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from document.models import Document
from permissions import IsMemberForProject
from project.models import Project
from document.serializers import DocumentSerializer

# class DocumentViewSet(viewsets.ModelViewSet):
#     queryset = Document.objects.all()
#     serializer_class = DocumentSerializer
#     permission_classes = [IsAuthenticated] #有待实现
#
#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)