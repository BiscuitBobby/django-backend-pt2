import json

import geohash
from firebase_admin import firestore, credentials, initialize_app
from google.cloud import firestore as geofirestore
from uuid import uuid4


cred = credentials.Certificate("Backend_pt2_app/admin-sdk.json")
__all__ = ['update_firebase_snapshot', ]
initialize_app(cred)

db = firestore.client()

def update_firebase_snapshot(location,
                             user='test1',
                             active=True,
                             event_name=None,
                             event_description=None,
                             event_type='food'):
    ###################################################


    doc_ref = db.collection('data').document(user)

    data = {
        "user": user,
        "location": geofirestore.GeoPoint(float(location[0]), float(location[1])),
        'active': active,
        'event_name': event_name,
        'event_description': event_description,
        'tag': event_type
    }

    doc_ref.set(data)

    print("Location data stored")
    ###########################################
    return 0


from firebase_admin import firestore

def get_all_geopoints(collection_name='data'):

    # Retrieve all documents from the collection
    collection_ref = db.collection(collection_name)
    documents = collection_ref.get()

    geopoints = []
    nearest = []

    # Process each document and extract GeoPoints
    for document in documents:
        doc_data = document.to_dict()
        location = doc_data.get('location')
        temp = dict()
        if location and isinstance(location, geofirestore.GeoPoint):
            geopoints.append(location)
            doc_data['password'] = 'nice try'
            nearest.append(doc_data)
    for i in range(len(nearest)):
        lat = nearest[i]['location'].latitude
        lng = nearest[i]['location'].longitude
        nearest[i]['lat'] = lat
        nearest[i]['lng'] = lng
        del nearest[i]['location']
        print('---')

    responce = dict()
    for i in nearest:
        responce[i['user']] = i
        del responce[i['user']]['user']
    print(responce)

    print(responce)

    return responce

def migrate_dummy_dat(x):
        for i in x:
            print(i, "-", x[i])
            update_firebase_snapshot([x[i]['lat'], x[i]['lng']], i, True, x[i]['event_name'], x[i]['event_description'],
                                     x[i]['tag'])
            print([x[i]['lat'], x[i]['lng']], i, True, x[i]['event_name'], x[i]['event_description'],
                                     x[i]['tag'])
