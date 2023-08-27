from rest_framework import serializers
from .models import *

class DesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Design
        exclude = ['is_deleted']


class DesignWithDataSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()

    class Meta:
        model = Design
        exclude = ['is_deleted']

    def get_data(self, design):
        latest_data = design.designhistory_set.first()
        return {
            'content': latest_data.content,
            'style': latest_data.style
        }


class DesignHistorySerializer(serializers.ModelSerializer):
    design = serializers.PrimaryKeyRelatedField(queryset=Design.objects.all())
    class Meta:
        model = DesignHistory
        fields = '__all__'
