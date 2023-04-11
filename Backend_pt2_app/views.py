import traceback

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from Backend_pt2_app.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


def index(request):
    return HttpResponse("welcome to the Index.")

@api_view(['GET'])
def getData(request):
    token = request.META.get('HTTP_TOKEN')
    if token == 'bob':
        items = User.objects.all()
        serializer = UserSerializer(items, many=True)
        return Response(serializer.data)
    else:
        return request.META.get("Invalid token")

@api_view(['POST'])
def addUser(request):
    serializer = UserSerializer(data=request.data)
    #password = str(PasswordHasher.encode("password", salt))
    try:
        if serializer.is_valid():
            serializer.save()
            print(serializer)
    except Exception as e:
        traceback.print_exc()
        print(serializer)
    return Response(serializer.data)
