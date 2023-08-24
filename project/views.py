from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from project.models import Project
from project.serializers import ProjectSerializer


# Create your views here.
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def project_view(request):
    if request.method == 'GET':
        try:
            projects_json = ProjectSerializer(instance=Project.objects.filter(is_deleted=False), many=True).data
            return Response(data=projects_json, status=status.HTTP_200_OK)
        except:
            return Response({'detail': '项目获取失败'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST':
        name = request.data.get('name')
        describe = request.data.get('describe')
        try:
            project = Project.objects.create(name=name, describe=describe)
            project_json = ProjectSerializer(instance=project, many=False).data
            return Response(data=project_json, status=status.HTTP_201_CREATED)
        except:
            return Response({'detail': '项目创建失败'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        id = request.data.get('id')
        name = request.data.get('name')
        describe = request.data.get('describe')
        try:
            project = Project.objects.get(id=id)
            project.name = name
            project.describe = describe
            project.save()
            project_json = ProjectSerializer(instance=project, many=False).data
            return Response(data=project_json, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'detail': '项目不存在'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': '项目修改失败'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        id = request.data.get('id')
        try:
            project = Project.objects.get(id=id)
            project.is_deleted = True
            project.save()
            return Response({'detail': '项目删除成功'}, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'detail': '项目不存在'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': '项目删除失败'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'detail': '无效的请求方式'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_single_project_view(request):
    id = request.query_params.get('id')
    try:
        project = Project.objects.get(id=id)
        project_json = ProjectSerializer(instance=project, many=False).data
        return Response(data=project_json, status=status.HTTP_200_OK)
    except Project.DoesNotExist:
        return Response({'detail': '项目不存在'}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'detail': '项目获取失败'}, status=status.HTTP_400_BAD_REQUEST)
