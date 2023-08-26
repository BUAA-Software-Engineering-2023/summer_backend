from rest_framework.permissions import BasePermission, SAFE_METHODS

from chat.models import Chat
from project.models import Project
from team.models import TeamMember


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user


class IsAdminOrMemberReadOnlyForTeam(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        kwargs = view.kwargs
        pk = kwargs.get('pk')
        try:
            relation = TeamMember.objects.get(team=pk, member=request.user)
            role = relation.role
            return role == 'admin' or role == 'creator' or request.method in SAFE_METHODS
        except TeamMember.DoesNotExist:
            return False


class IsAdminForTeam(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        kwargs = view.kwargs
        pk = kwargs.get('pk')
        try:
            relation = TeamMember.objects.get(team=pk, member=request.user)
            role = relation.role
            return role == 'admin' or role == 'creator'
        except TeamMember.DoesNotExist:
            return False


class IsCreatorForTeam(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        kwargs = view.kwargs
        pk = kwargs.get('pk')
        try:
            relation = TeamMember.objects.get(team=pk, member=request.user)
            role = relation.role
            return role == 'creator'
        except TeamMember.DoesNotExist:
            return False


class IsAdminForTeamInvite(BasePermission):
    message = '请联系管理员'

    def has_permission(self, request, view):
        if not request.user:
            return False
        pk = request.data.get('team')
        try:
            relation = TeamMember.objects.get(team=pk, member=request.user)
            role = relation.role
            return role == 'admin' or role == 'creator'
        except TeamMember.DoesNotExist:
            return False


class IsMemberForProject(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        team = request.data.get('team')
        if team:
            try:
                TeamMember.objects.get(team=team, member=request.user)
                return True
            except TeamMember.DoesNotExist:
                return False
        else:
            kwargs = view.kwargs
            pk = kwargs.get('pk')
            try:
                TeamMember.objects.get(team__project=pk, member=request.user)
                return True
            except TeamMember.DoesNotExist:
                return False

class IsMemberForChat(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        team = request.data.get('team')
        if team:
            try:
                TeamMember.objects.get(team=team, member=request.user)
                return True
            except TeamMember.DoesNotExist:
                return False
        else:
            kwargs = view.kwargs
            pk = kwargs.get('pk')
            try:
                TeamMember.objects.get(team__chat=pk, member=request.user)
                return True
            except TeamMember.DoesNotExist:
                return False