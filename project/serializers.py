from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        exclude = ['is_deleted', 'preview_designs']  # 结果中不包含的字段


