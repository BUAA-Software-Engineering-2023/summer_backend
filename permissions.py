from rest_framework.permissions import BasePermission, SAFE_METHODS

from chat.models import Chat
from document.models import Document
from summer_backend.settings import SECRET_KEY
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
        except Exception:
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
        except Exception:
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
        except Exception:
            return False


class IsAdminForTeamInvite(BasePermission):
    message = '请联系管理员'

    def has_permission(self, request, view):
        if not request.user:
            return False
        pk = request.data.get('team') or request.query_params.get('team')
        try:
            relation = TeamMember.objects.get(team=pk, member=request.user)
            role = relation.role
            return role == 'admin' or role == 'creator'
        except Exception:
            return False


class IsMemberForProject(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        team = request.data.get('team') or request.query_params.get('team')
        if team:
            try:
                TeamMember.objects.get(team=team, member=request.user)
                return True
            except Exception:
                return False
        else:
            kwargs = view.kwargs
            pk = kwargs.get('pk') or request.query_params.get('project') or request.data.get('project')
            try:
                TeamMember.objects.get(team__project=pk, member=request.user)
                return True
            except Exception:
                return False


class IsMemberForChat(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        team = request.data.get('team') or request.query_params.get('team')
        if team:
            try:
                TeamMember.objects.get(team=team, member=request.user)
                return True
            except Exception:
                return False
        return False

class IsMemberOfChat(BasePermission):
    def has_permission(self, request, view):
        kwargs = view.kwargs
        pk = kwargs.get('pk')
        try:
            Chat.objects.get(pk=pk, members=request.user)
            return True
        except Exception:
            return False

class IsAdminOfChat(BasePermission):
    def has_permission(self, request, view):
        kwargs = view.kwargs
        pk = kwargs.get('pk')
        try:
            Chat.objects.get(pk=pk, admin=request.user)
            return True
        except Exception:
            return False

class IsMemberForDocument(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        project = request.data.get('project') or request.query_params.get('project')
        if project:
            try:
                TeamMember.objects.get(team__project=project, member=request.user)
                return True
            except Exception:
                return False
        else:
            kwargs = view.kwargs
            pk = kwargs.get('pk') or request.data.get('document') or request.query_params.get('document')
            try:
                TeamMember.objects.get(team__project__document=pk, member=request.user)
                return True
            except Exception:
                return False


class IsMemberForDesign(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        project = request.data.get('project') or request.query_params.get('project')
        if project:
            try:
                TeamMember.objects.get(team__project=project, member=request.user)
                return True
            except Exception:
                return False
        else:
            kwargs = view.kwargs
            pk = kwargs.get('pk') or request.query_params.get('design') or request.data.get('design')
            try:
                TeamMember.objects.get(team__project__design=pk, member=request.user)
                return True
            except Exception:
                return False


class IsMemberOrVisitorReadOnlyForDocument(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            try:
                document = request.query_params.get('document') or request.data.get('document')
                if document:
                    document = Document.objects.get(pk=document)
                    return document.is_shared
                else:
                    return False
            except Exception:
                return False
        document = request.query_params.get('document') or request.data.get('document')
        if document:
            try:
                TeamMember.objects.get(team__project__document=document, member=request.user)
                return True
            except TeamMember.DoesNotExist:
                return False
        else:
            return False


class IsSecretKeyAuthorized(BasePermission):
    def has_permission(self, request, view):
        secret_key = request.data.get('SECRET_KEY') or request.query_params.get('SECRET_KEY')
        if secret_key:
            if secret_key == SECRET_KEY:
                return True
            else:
                return False
        else:
            return False


class IsAdminForDocument(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        document = request.data.get('document') or request.query_params.get('document')
        if document:
            try:
                relation = TeamMember.objects.get(team__project__document=document, member=request.user)
                role = relation.role
                return role == 'admin' or role == 'creator'
            except TeamMember.DoesNotExist:
                return False
        else:
            team = request.data.get('team') or request.query_params.get('team')
            if team:
                try:
                    relation = TeamMember.objects.get(team=team, member=request.user)
                    role = relation.role
                    return role == 'admin' or role == 'creator'
                except Exception:
                    return False