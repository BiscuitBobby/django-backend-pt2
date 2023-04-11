import traceback
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from Backend_pt2_app.models import User
from . import salt
from .encryption import PBKDF2WrappedSHA1PasswordHasher


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


def index(request):
    return HttpResponse("welcome to the Index.")

'''@login_required
def my_protected_view(request):
    return render(request, 'protected.html', {'current_user': request.user})
'''
@api_view(['GET'])
def getData(request):
    token = request.META.get('HTTP_TOKEN')
    if token == 'bob':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    else:
        return request.META.get("Invalid token")

@api_view(['POST'])
def addUser(request):
    password_hasher = PBKDF2WrappedSHA1PasswordHasher()
    data = request.data
    data["password"] = password_hasher.encode(data["password"], salt.salt)
    serializer = UserSerializer(data=data)
    try:
        if serializer.is_valid():
            serializer.save()
            print(serializer)
        else:
            print('invalid')
            return Response(serializer.errors)
    except Exception as e:
        traceback.print_exc()
        print(serializer)
        return Response(e)

    return Response(serializer.data)
