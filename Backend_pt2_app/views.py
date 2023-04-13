import json
import traceback
from django.http import HttpResponse
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from Backend_pt2_app.models import User
from . import salt
from .encryption import PBKDF2WrappedSHA1PasswordHasher
from firebase_admin import firestore, initialize_app
from firebase_admin import credentials
from django.http import JsonResponse
from .firebase_functions import send_to_firebase
from django.shortcuts import render, redirect


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


def index(request):
    return HttpResponse("welcome to the Index.")

@api_view(['POST'])
def authenticate(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Invalid credentials'})
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key})

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
            try:
                send_to_firebase(data["name"], data["password"])
            except Exception as e:
                traceback.print_exc()
                print(serializer)
                return Response(e, serializer.data)
            print(serializer)
        else:
            print('invalid')
            return Response(serializer.errors)
    except Exception as e:
        traceback.print_exc()
        print(serializer)
        return Response(e)

    return Response(serializer.data)


'''@api_view(['GET'])
def getLoc(request):
    user = request.META.get('HTTP_USER')
    db = firestore.client()
    ans = dict()
    for i in ['geopoints']:
        notifications_ref = db.collection(i)
        query = notifications_ref.where('user', '==', user)
        docs = query.get()
        for doc in docs:
            print(f'Document ID: {doc.id}')
            data = doc.to_dict()
            print(f'Document data: {doc.to_dict()}')
            if 'geopoint' in data:
                data['geopoint'] = {
                    'latitude': data['geopoint'].latitude,
                    'longitude': data['geopoint'].longitude,
                }
            ans.update(data)
        print(data['geopoint'])
        print(ans)
    data_json = json.dumps(ans)
    return JsonResponse(data_json, safe=False)'''


@api_view(['GET'])
def nearEvents(request):
    location = request.META.get('HTTP_location')
    print(location)
    temp_response = {
        'user0': {'event_name': 'An event', 'event_description': 'this is a description of the event',
                  'tag': 'food', 'lat': 9.123792057073985, 'lng': 76.52561187744142},
        'user1': {'event_name': 'An event', 'event_description': 'this is a description of the event',
                  'tag': 'food', 'lat': 9.09226561408639, 'lng': 76.4861297607422},
        'user2': {'event_name': 'An event', 'event_description': 'this is a description of the event',
                  'tag': 'food', 'lat': 9.098876227646803, 'lng': 76.5666389465332},
        'user3': {'event_name': 'An event', 'event_description': 'this is a description of the event',
                  'tag': 'shopping', 'lat': 9.131080032196818, 'lng': 76.50466918945314},
        'user4': {'event_name': 'An event', 'event_description': 'this is a description of the event',
                  'tag': 'shopping', 'lat': 9.112097088234403, 'lng': 76.51016235351564},
        'user5': {'event_name': 'An event', 'event_description': 'this is a description of the event',
                  'tag': 'sport', 'lat': 9.085824386028294, 'lng': 76.50827407836915},
        'user6': {'event_name': 'An event', 'event_description': 'this is a description of the event',
                  'tag': 'sport', 'lat': 9.10836817706563, 'lng': 76.48389816284181},
        'user7': {'event_name': 'An event', 'event_description': 'this is a description of the event',
                  'tag': 'sport', 'lat': 9.103622233852995, 'lng': 76.47462844848634},
    }
    data_json = json.dumps(temp_response)
    return JsonResponse(data_json, safe=False)


@api_view(['GET'])
def login(request):
    s = ''
    with open("Backend_pt2_app/login.html", "r") as file:
        x = file.readlines()
        for i in x:
            s += i
    response = HttpResponse(s)
    response['strict-transport-security'] = 'max-age=31536000; includeSubDomains'
    return response
