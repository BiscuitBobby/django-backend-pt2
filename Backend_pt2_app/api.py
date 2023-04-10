from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import serializers
from models import User
from django.http import JsonResponse

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
