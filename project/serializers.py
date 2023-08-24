from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Mata:
        model = Project
        exclude = ['id', 'is_deleted']  # 结果中不包含的字段
        depth = 1  # 设置外键遍历的深度
