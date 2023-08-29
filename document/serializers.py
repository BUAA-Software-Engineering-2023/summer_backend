from rest_framework import serializers
from .models import Document, DocumentHistory


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class DocumentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentHistory
        fields = '__all__'


class DocumentWithDataSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = Document
        exclude = ['is_deleted']

    def get_content(self, document):
        latest_data = document.documenthistory_set.filter(is_deleted=False).first()
        return latest_data.content

