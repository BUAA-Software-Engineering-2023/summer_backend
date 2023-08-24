from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        if validated_data['password'] != validated_data.pop('confirm_password'):
            raise serializers.ValidationError("两次密码不一致")
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)