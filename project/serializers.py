from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        exclude = ['id', 'is_deleted']  # 结果中不包含的字段


# class ProjectSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Project
#         fields = ['id', 'name', 'describe', 'is_deleted', 'create_time', 'update_time', 'team']


