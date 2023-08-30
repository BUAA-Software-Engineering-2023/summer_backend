from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from permissions import *
from .serializers import *
from .models import *
from django.db.models import Q


class TeamListCreateView(generics.ListCreateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_queryset(self):
        user = self.request.user
        return Team.objects.filter(members__id=user.id)

    def perform_create(self, serializer):
        user = self.request.user
        team = serializer.save()
        TeamMember.objects.create(team=team, member=user, role='creator')

        # 创建群聊
        data = self.request.data
        chat = Chat.objects.create(name=data['name'], team=team, type='group', priority=999)
        chat.members.set([user])

class TeamRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeamWithMemberSerializer
    permission_classes = [IsAdminOrMemberReadOnlyForTeam]
    def get_queryset(self):
        user = self.request.user
        return Team.objects.filter(members__id=user.id)
    def perform_update(self, serializer):
        team = serializer.save()
        name = self.request.data.get('name')
        if name:
            chat = team.chat_set.get(priority=999)
            chat.name = name
            chat.save()

@api_view(['POST'])
@permission_classes([IsAdminForTeam])
def add_admin_view(request, pk):
    member = request.data.get('member')
    try:
        relation = TeamMember.objects.get(team=pk, member=member)
    except TeamMember.DoesNotExist:
        return Response({'detail': '不可授予非团队成员管理员权限'}, status=status.HTTP_400_BAD_REQUEST)
    relation.role = 'admin'
    relation.save()
    return Response(None, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsCreatorForTeam])
def remove_admin_view(request, pk):
    member = request.data.get('member')
    try:
        relation = TeamMember.objects.get(team=pk, member=member)
    except TeamMember.DoesNotExist:
        return Response({'detail': '无需取消'}, status=status.HTTP_400_BAD_REQUEST)
    relation.role = 'member'
    relation.save()
    return Response(None, status=status.HTTP_200_OK)

class TeamInviteListCreateView(generics.ListCreateAPIView):
    serializer_class = TeamInviteSerializer
    permission_classes = [IsAdminForTeamInvite]

    def get_queryset(self):
        team = self.request.data.get('team') or self.request.query_params.get('team')
        return TeamInvite.objects.filter(team=team)
    def perform_create(self, serializer):
        team = self.request.data.get('team')
        invitee = self.request.data.get('invitee')
        invite = TeamInvite.objects.filter(Q(team=team) & Q(invitee=invitee),
                                           Q(status='send') & ~Q(team__members=invitee))
        if invite:
            raise serializers.ValidationError({'detail': '无需发送邀请'})
        serializer.save()

@api_view(['POST'])
def resolve_invite_view(request, pk):
    accept = request.data.get('accept')
    new_status = 'accept' if accept else 'reject'
    try:
        invite = TeamInvite.objects.get(pk=pk)
    except TeamInvite.DoesNotExist:
        return Response({'detail': '此邀请无效'}, status=status.HTTP_400_BAD_REQUEST)
    if invite.status != 'send':
        return Response({'detail': '此邀请已失效'}, status=status.HTTP_400_BAD_REQUEST)
    if accept:
        team = invite.team
        invitee = invite.invitee
        TeamMember.objects.create(team=team, member=invitee)
        # 添加到群聊
        chat = Chat.objects.get(team=team, priority=999)
        chat.members.add(invitee)


    invite.status = new_status
    invite.save()
    return Response(TeamInviteSerializer(invite).data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAdminForTeam])
def remove_member_view(request, pk):
    member = request.data.get('member')
    try:
        relation = TeamMember.objects.get(team=pk, member=member).delete()
        # 移出群聊
        chat = Chat.objects.get(team=pk, priority=999)
        chat.members.remove(member)
    except TeamMember.DoesNotExist:
        return Response({'detail': '无需移除'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(None, status=status.HTTP_200_OK)
