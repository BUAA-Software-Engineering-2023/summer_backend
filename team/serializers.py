from rest_framework import serializers
from .models import Team
from user.serializers import UserSerializer

class TeamSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, required=False)
    class Meta:
        model = Team
        fields = '__all__'