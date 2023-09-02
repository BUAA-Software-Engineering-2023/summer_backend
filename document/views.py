from django.utils import timezone
import jwt
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from message.models import Message
from permissions import IsMemberForDocument, IsMemberOrVisitorReadOnlyForDocument, \
    IsSecretKeyAuthorized, IsAdminForDocument, IsAuthenticated
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
        folder = self.request.data.get('folder')
        if folder:
            serializer.save(
                title=self.request.data.get('title'),
                project=Project.objects.get(pk=self.request.data.get('project')),
                folder=DocumentFolder.objects.get(pk=self.request.data.get('folder'))
            )
            DocumentHistory.objects.create(
                document=serializer.instance,
                content=''
            )
        else:
            serializer.save(
                title=self.request.data.get('title'),
                project=Project.objects.get(pk=self.request.data.get('project'))
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
    return Response(data={'detail': '已授权阅读', 'content': document_history.first().content, 'editable': editable, 'title': document.title},
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
    # DocumentHistory.objects.filter(created_time__gt=document_history.created_time,
    #                                document=document_history.document).update(
    #     is_deleted=True)
    document_history = DocumentHistory.objects.create(
        document=document_history.document,
        content=document_history.content
    )
    document_history.created_time=timezone.now() + timezone.timedelta(seconds=10)
    document_history.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsSecretKeyAuthorized])
def migrate_documents_view(request):
    data = DocumentWithDataSerializer(instance=Document.objects.filter(is_deleted=False), many=True).data
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsSecretKeyAuthorized | IsMemberOrVisitorReadOnlyForDocument])
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
        return DocumentFolder.objects.filter(project=project, is_deleted=False)

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


@api_view(['GET'])
@permission_classes([IsMemberForDocument])
def get_document_tree_view(request):
    project = Project.objects.get(pk=(request.query_params.get('project') or request.data.get('project')))
    document_folders = DocumentFolder.objects.filter(project=project, is_deleted=False)
    folder_data = DocumentFolderTreeSerializer(instance=document_folders, many=True).data
    documents = Document.objects.filter(project=project, is_deleted=False, folder=None)
    document_data = DocumentSerializer(instance=documents, many=True).data
    data = folder_data + document_data
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_template_view(request):
    documents = Document.objects.filter(project__isnull=True, is_deleted=False)
    data = DocumentSerializer(instance=documents, many=True).data
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsMemberForDocument])
def document_mention_view(request):
    receiver = request.data.get('receiver')
    document = request.data.get('document')
    try:
        receiver = User.objects.get(pk=receiver)
    except User.DoesNotExist:
        return Response(data={'detail': '无对应用户'}, status=status.HTTP_404_NOT_FOUND)
    sender_name = request.user.name
    document = Document.objects.get(pk=document)
    document_name = document.title
    Message.objects.create(
        receiver=receiver,
        content=f'{sender_name}在文件{document_name}中@了你‘',
        document=document
    )
    return Response(data={'detail': '已@用户'}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAdminForDocument])
def deauthorize_share_view(request):
    document = Document.objects.get(pk=request.data.get('document'))
    document.is_shared = False
    document.is_editable = False
    document.save()
    return Response(status=status.HTTP_200_OK)
