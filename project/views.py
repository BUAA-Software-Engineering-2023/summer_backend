from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from design.models import Design, DesignHistory
from document.models import Document, DocumentHistory, DocumentFolder
from permissions import IsMemberForProject
from project.models import Project
from .serializers import ProjectSerializer


# Create your views here.
@api_view(['GET'])
@permission_classes([IsMemberForProject])

def get_deleted_project_view(request):
    try:
        projects_json = ProjectSerializer(instance=Project.objects.filter(is_deleted=True), many=True).data
        return Response(data=projects_json, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': '项目获取失败,' + e.args[0]}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsMemberForProject])
def restore_project_view(request):
    id = request.data.get('id')
    try:
        project = Project.objects.get(id=id)
        project.is_deleted = False
        project.save()
        return Response({'detail': '项目恢复成功'}, status=status.HTTP_200_OK)
    except Project.DoesNotExist:
        return Response({'detail': '项目不存在'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'detail': '项目恢复失败,' + e.args[0]}, status=status.HTTP_400_BAD_REQUEST)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsMemberForProject]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = '__all__'
    ordering = ['create_time']

    def get_queryset(self):
        team = self.request.data.get('team') or self.request.query_params.get('team')
        if team:
            projects = Project.objects.filter(team=team, is_deleted=False)
        else:
            projects = Project.objects.filter(is_deleted=False)
        return projects

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@api_view(['POST'])
@permission_classes([IsMemberForProject])
def duplicate_project_view(request):
    id = request.data.get('id')
    try:
        project = Project.objects.get(id=id)
        new_project = Project.objects.create(name=project.name + '副本',
                                             describe=project.describe,
                                             team=project.team)
        designs = project.design_set.all()
        for design in designs:
            new_design = Design.objects.create(title=design.title,
                                               describe=design.describe,
                                               project=new_project)
            design.designhistory_set.all()
            for history in design.designhistory_set.all():
                DesignHistory.objects.create(design=new_design,
                                             content=history.content,
                                             style=history.style)
        for document in project.document_set.all():
            new_document = Document.objects.create(title=document.title,
                                                   project=new_project)
            document.documenthistory_set.all()
            for history in document.documenthistory_set.all():
                DocumentHistory.objects.create(document=new_document,
                                               content=history.content)
        for document_folder in project.documentfolder_set.all():
            DocumentFolder.objects.create(name=document_folder.name,
                                          project=new_project)
        return Response({'detail': '项目复制成功'}, status=status.HTTP_200_OK)
    except Project.DoesNotExist:
        return Response({'detail': '项目不存在'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'detail': '项目复制失败,' + e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
