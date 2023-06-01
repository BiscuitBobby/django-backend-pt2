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
from . import salt, encryption
from .encryption import PBKDF2WrappedSHA1PasswordHasher
from django.http import JsonResponse
from .firebase_functions import update_firebase_snapshot, get_all_geopoints, migrate_dummy_dat
from django.shortcuts import render, redirect

with open('Backend_pt2_app/temp.json', 'r') as file:
    # Load the JSON data into a dictionary
    temp_response = json.load(file)
    print(temp_response)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


def index(request):
    return HttpResponse("welcome to the Index.")

@api_view(['POST'])
def auth(request):
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
    global temp_response
    location = request.META.get('HTTP_location')
    print(location)

    data_json = get_all_geopoints()
    return JsonResponse(data_json, safe=False)


@api_view(['POST'])
def update_event(request):
    global temp_response
    token = request.META.get('HTTP_TOKEN')
    username = request.META.get('HTTP_USERNAME')
    tag = request.META.get('HTTP_TYPE')
    eventdetails = request.META.get('HTTP_EVENTDETAILS')
    eventname = request.META.get('HTTP_EVENTNAME')
    lat = request.META.get('HTTP_LAT')
    long = request.META.get('HTTP_LONG')
    #print(request.META)
    # migrate_dummy_dat(temp_response)
    try:
        user = str((Token.objects.get(key=token)).user).strip()
        if username == user:
            temp_response[user] = {'event_name': eventname, 'event_description': eventdetails,
                                         'tag': tag, 'lat': lat, 'lng': long}
            print(temp_response[user])
            with open('Backend_pt2_app/temp.json', 'w') as file:
                # Write the updated JSON data to the file
                json.dump(temp_response, file)
                update_firebase_snapshot([lat, long], user, True, eventname, eventdetails)
                get_all_geopoints('data')
    except Exception as e:
        traceback.print_exc()
        return Response(traceback)
    data_json = json.dumps(temp_response)
    return Response(data_json)

@api_view(['GET'])
def login(request):
    page_render = encryption.secure_html_view("Backend_pt2_app/login.html")
    return page_render
