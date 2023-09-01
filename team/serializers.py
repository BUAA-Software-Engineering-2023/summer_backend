from rest_framework import serializers
from .models import *
from user.serializers import UserSerializer

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        exclude = ['members','is_deleted']


class TeamWithMemberSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    class Meta:
        model = Team
        exclude = ['is_deleted']
        extra_kwargs = {'members': {'read_only': True}}
    def get_members(self, team):
        members = team.members.all()
        members = UserSerializer(members, many=True)
        for member in members.data:
            relation = TeamMember.objects.get(team=team, member=member['id'])
            member['role'] = relation.get_role_display()
        return members.data

class TeamInviteSerializer(serializers.ModelSerializer):
    team = TeamSerializer()
    invitee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    status = serializers.SerializerMethodField()
    class Meta:
        model = TeamInvite
        fields = '__all__'
        extra_kwargs = {'members': {'read_only': True}}

    def get_status(self, team_invite):
        return team_invite.get_status_display()