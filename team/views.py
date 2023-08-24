import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import viewsets

from .serializers import *
from .models import *


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_queryset(self):
        user = self.request.user
        return Team.objects.filter(members__id=user.id)

    def perform_create(self, serializer):
        user = self.request.user
        team = serializer.save()
        TeamMember.objects.create(team=team, member=user, role='creator')
