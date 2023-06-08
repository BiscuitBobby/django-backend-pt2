import json
import traceback
from django.http import HttpResponse
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from Backend_pt2_app.models import User
from . import salt
from .encryption import PBKDF2WrappedSHA1PasswordHasher
from django.http import JsonResponse
from .firebase_functions import update_firebase_snapshot, get_all_geopoints, join_event, leave_event

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
    try:
        expiry = float(request.META.get('HTTP_EXPIRY'))
        print('expiry:', expiry)
    except:
        print('couldnt find expiry')
        expiry = 1
    #print(request.META)
    # migrate_dummy_dat(temp_response)
    try:
        token_obj = Token.objects.get(key=token)  # Retrieve the Token object using the provided token
        obj = token_obj.user  # Get the User object associated with the token
        user = obj.username
        print('generated token')
        print(user,'---',username)
        if username == user:
            update_firebase_snapshot([lat, long], user, True, eventname, eventdetails, tag, expiry)
            print('sdvasdvad')
            get_all_geopoints('data')
            print('sdvasdvad')
        else:
            print('invalid user')
    except Exception as e:
        traceback_str = traceback.format_exc()  # Get the traceback as a string
        print(traceback_str)  # Optional: Print the traceback for debugging
        return Response(traceback_str)
    data_json = json.dumps(temp_response)
    return Response(data_json)


@api_view(['POST'])
def event_join(request):
    data = json.loads(request.body)
    token = data['token']
    username = data['username']
    eventid = data['eventid']
    try:
        token_obj = Token.objects.get(key=token)
        obj = token_obj.user
        user = obj.username
        if username == user:
            join_event(eventid)
            return Response({"joined user"})
    except:
        print('auth failure')
        return Response({"failed to join"})

    @api_view(['POST'])
    def event_leave(request):
        data = json.loads(request.body)
        token = data['token']
        username = data['username']
        eventid = data['eventid']
        try:
            token_obj = Token.objects.get(key=token)
            obj = token_obj.user
            user = obj.username
            if username == user:
                leave_event(eventid)
                return Response({"user left"})
        except:
            print('auth failure')
            return Response({"failed to leave"})


@api_view(['POST'])
def register(request):
    data = json.loads(request.body)
    email = data['email']
    username = data['username']
    pswrd = data['password']

    print(username, email)
    user = User.objects.create_user(email=email, password=pswrd, username=username)
    user.save()
    print('created user: '+username)
    return Response("created user")
