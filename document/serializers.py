from rest_framework import serializers
from .models import Project, Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'created_by', 'project', 'created_at', 'last_modified']