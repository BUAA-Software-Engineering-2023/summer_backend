import jwt
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from permissions import IsMemberForDocument, IsMemberOrVisitorReadOnlyForDocument, \
    IsSecretKeyAuthorized, IsAdminForDocument
from project.models import Project
from summer_backend import settings
from user.models import User
from .models import Document, DocumentHistory, DocumentFolder
from .serializers import DocumentSerializer, DocumentHistorySerializer, DocumentWithDataSerializer, \
    DocumentFolderTreeSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsMemberForDocument]

    def get_queryset(self):
        project = Project.objects.get(pk=(self.request.query_params.get('project') or self.request.data.get('project')))
        return Document.objects.filter(project=project, is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(
            title=self.request.data.get('title'),
            project=Project.objects.get(pk=self.request.data.get('project')),
            folder=DocumentFolder.objects.get(pk=self.request.data.get('folder'))
        )
        DocumentHistory.objects.create(
            document=serializer.instance,
            content=''
        )

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.documenthistory_set.update(is_deleted=True)
        instance.save()


# 需加权限校验,是不是管理员或项目创建者
@api_view(['PATCH'])
@permission_classes([IsAdminForDocument])
def authorize_share_view(request):
    document = Document.objects.get(pk=request.data.get('document'))
    editable = request.data.get('editable')
    document.is_shared = True
    document.is_editable = editable
    document.save()
    return Response(status=status.HTTP_200_OK)


# 需加权限校验，是不是团队成员或游客只读
@api_view(['GET'])
@permission_classes([IsMemberOrVisitorReadOnlyForDocument])
def read_document_view(request):
    document = Document.objects.get(pk=request.query_params.get('document'))
    document_history = DocumentHistory.objects.filter(document=document, is_deleted=False).order_by('-created_time')
    if not request.user:
        editable = document.is_editable
    else:
        editable = True
    return Response(data={'detail': '已授权阅读', 'content': document_history.first().content, 'editable': editable},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsMemberForDocument])
def get_histories_view(request):
    document = Document.objects.get(pk=request.query_params.get('document'))
    document_histories = DocumentHistory.objects.filter(document=document, is_deleted=False).order_by('-created_time')
    data = DocumentHistorySerializer(instance=document_histories, many=True).data
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsMemberForDocument])
def restore_history_view(request):
    document_history = DocumentHistory.objects.get(pk=request.data.get('document_history'))
    DocumentHistory.objects.filter(created_time__gt=document_history.created_time,
                                   document=document_history.document).update(
        is_deleted=True)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsSecretKeyAuthorized])
def migrate_documents_view(request):
    data = DocumentWithDataSerializer(instance=Document.objects.all(), many=True).data
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsSecretKeyAuthorized or IsMemberOrVisitorReadOnlyForDocument])
def save_document_view(request):
    try:
        document = Document.objects.get(pk=request.data.get('document'))
    except Document.DoesNotExist:
        return Response(data={'detail': '文档不存在'}, status=status.HTTP_404_NOT_FOUND)
    content = request.data.get('content')
    document_history = DocumentHistory.objects.create(
        document=document,
        content=content
    )
    data = DocumentHistorySerializer(instance=document_history).data
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsSecretKeyAuthorized])
def synchronize_document_view(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response(data={'detail': '文档不存在'}, status=status.HTTP_404_NOT_FOUND)
    data = DocumentWithDataSerializer(instance=document).data
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsSecretKeyAuthorized])
def authorization_check_view(request):
    token = request.data.get('token')
    if not token:
        try:
            document = Document.objects.get(pk=request.data.get('document'))
        except Document.DoesNotExist:
            return Response(data={'has_permission': False}, status=status.HTTP_200_OK)
        read_only = request.data.get('readOnly')
        if read_only:
            permission = document.is_shared
        else:
            permission = document.is_editable
        return Response(data={'has_permission': permission}, status=status.HTTP_200_OK)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        user_id = payload['id']
        user = User.objects.get(pk=user_id)
        return Response(data={'has_permission': True}, status=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError:
        return Response(data={'has_permission': False}, status=status.HTTP_200_OK)
    except (jwt.DecodeError, User.DoesNotExist):
        return Response(data={'has_permission': False}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(data={'has_permission': False}, status=status.HTTP_200_OK)


class DocumentFolderViewSet(viewsets.ModelViewSet):
    queryset = DocumentFolder.objects.all()
    serializer_class = DocumentFolderTreeSerializer
    permission_classes = [IsMemberForDocument]

    def get_queryset(self):
        project = Project.objects.get(pk=(self.request.query_params.get('project') or self.request.data.get('project')))
        return DocumentFolder.objects.filter(project=project)

    def perform_create(self, serializer):
        serializer.save(
            name=self.request.data.get('name'),
            project=Project.objects.get(pk=self.request.data.get('project'))
        )

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        instance.document_set.update(is_deleted=True)
        documents = instance.document_set.all()
        for document in documents:
            document.documenthistory_set.update(is_deleted=True)
