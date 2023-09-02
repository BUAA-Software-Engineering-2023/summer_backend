from rest_framework import serializers
from .models import *


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
        if not latest_data:
            return None
        return latest_data.content


class DocumentFolderTreeSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = DocumentFolder
        fields = '__all__'

    def get_documents(self, document_folder):
        documents = Document.objects.filter(folder=document_folder, is_deleted=False)
        return DocumentSerializer(documents, many=True).data
