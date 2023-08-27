from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from permissions import IsAdminForTeam, IsMemberForDocument, IsMemberOrVisitorReadOnlyForDocument
from project.models import Project
from .models import Document, DocumentHistory
from .serializers import DocumentSerializer, DocumentHistorySerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsMemberForDocument]

    def get_queryset(self):
        project = Project.objects.get(pk=self.request.query_params.get('project'))
        return Document.objects.filter(project=project)

    def perform_create(self, serializer):
        serializer.save(
            title=self.request.data.get('title'),
            project=Project.objects.get(pk=self.request.data.get('project_id'))
        )
        DocumentHistory.objects.create(
            document=serializer.instance,
            content=''
        )

    def perform_destroy(self, serializer):
        serializer.save(is_deleted=True)
        DocumentHistory.objects.filter(document=serializer.instance).update(is_deleted=True)


# 需加权限校验,是不是管理员或项目创建者
@api_view(['PATCH'])
@permission_classes([IsAdminForTeam])
def authorize_share_view(request):
    document = Document.objects.get(pk=request.data.get('pk'))
    document.is_shared = True
    document.save()
    return Response(status=status.HTTP_200_OK)


# 需加权限校验，是不是团队成员或游客只读
@api_view(['GET'])
@permission_classes([IsMemberOrVisitorReadOnlyForDocument])
def read_document_view(request):
    document = Document.objects.get(pk=request.query_params.get('pk'))
    document_history = DocumentHistory.objects.filter(document=document, is_deleted=False).order_by('-created_time')
    return Response(data=document_history.first().content, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminForTeam])
def get_histories_view(request):
    document = Document.objects.get(pk=request.query_params.get('pk'))
    document_histories = DocumentHistory.objects.filter(document=document, is_deleted=False).order_by('-created_time')
    data = DocumentSerializer(instance=document_histories, many=True)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAdminForTeam])
def restore_history_view(request):
    document_history = DocumentHistory.objects.filter(pk=request.data.get('pk'))
    DocumentHistory.objects.filter(document__update_time__gt=document_history.update_time.timestamp()).update(is_deleted=True)
