from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from permissions import IsMemberForProject
from project.models import Project
from .serializers import ProjectSerializer


# Create your views here.
@api_view(['GET'])
def get_deleted_project_view(request):
    try:
        projects_json = ProjectSerializer(instance=Project.objects.filter(is_deleted=True), many=True).data
        return Response(data=projects_json, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': '项目获取失败,' + e.args[0]}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
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

    def get_queryset(self):
        team = self.request.data.get('team')
        if team:
            projects = Project.objects.filter(team=team, is_deleted=False)
        else:
            projects = Project.objects.filter(is_deleted=False)
        return projects

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()




