import datetime
from firebase_admin import firestore, credentials, initialize_app
from google.cloud import firestore as geofirestore

cred = credentials.Certificate("Backend_pt2_app/admin-sdk.json")
__all__ = ['update_firebase_snapshot', ]
initialize_app(cred)

db = firestore.client()


def update_firebase_snapshot(location,
                             user='test1',
                             active=True,
                             event_name=None,
                             event_description=None,
                             event_type='food',
                             expiry=1):  # 1 = 24 hours
    ###################################################

    doc_ref = db.collection('data').document(user)

    data = {
        "user": user,
        "location": geofirestore.GeoPoint(float(location[0]), float(location[1])),
        'active': active,
        'event_name': event_name,
        'event_description': event_description,
        'tag': event_type,
        'created': str(datetime.datetime.now()),
        'expiry': str((datetime.datetime.now()) + datetime.timedelta(hours=expiry)),
        'lobby': 0,
        'lobby_size': 10
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
    import datetime

    for document in documents:
        doc_data = document.to_dict()
        location = doc_data.get('location')
        if location and isinstance(location, geofirestore.GeoPoint):
            geopoints.append(location)
            doc_data['password'] = 'nice try'
            try:
                expiry_str = doc_data.get('expiry')
                expiry_timedelta = datetime.datetime.strptime(expiry_str, '%Y-%m-%d %H:%M:%S.%f')
                current_datetime = datetime.datetime.now()
                print("Expiry String:", expiry_str)
                print("Expiry Timedelta:", expiry_timedelta)
                print("Current Datetime:", current_datetime)

                if expiry_timedelta <= current_datetime:
                    document.reference.delete()
                    print("Document deleted.")
                else:
                    nearest.append(doc_data)
                    print("Document added to nearest.")

            except Exception as e:
                print("Error occurred:", str(e))
                print('No expiry')
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

    return responce

def join_event(event,user='test0'):
    print("--Join event--")
    doc_ref = db.collection('data').document(event)
    documents = doc_ref.get().to_dict()

    try:
        if user not in documents['users']:
            documents['lobby'] += 1
            print(documents['lobby'])
            documents['users'].append(user)
        else:
            print('already in')
            return 'already in'
    except:
        documents['lobby_size'] = 0
        documents['lobby'] = 1
        documents['users'] = [user, ]
    doc_ref.set(documents)

    print("--------------")
    print("--great success--")
    return 'great success'
    ###########################################


def leave_event(event, user='test0'):
    print("--Join event--")
    doc_ref = db.collection('data').document(event)
    documents = doc_ref.get().to_dict()

    try:
        if user in documents['users']:
            documents['lobby'] -= 1
            print(documents['lobby'])
            documents['users'].remove(user)
        else:
            print('already out')
            return 'already out'
    except:
        documents['lobby_size'] = 0
        documents['lobby'] = 0
        documents['users'] = []
    doc_ref.set(documents)

    print("--------------")
    print("--great success--")
    return 'great success'
    ###########################################


def migrate_dummy_dat(x):
    for i in x:
        print(i, "-", x[i])
        update_firebase_snapshot([x[i]['lat'], x[i]['lng']], i, True, x[i]['event_name'], x[i]['event_description'],
                                 x[i]['tag'])
        print([x[i]['lat'], x[i]['lng']], i, True, x[i]['event_name'], x[i]['event_description'],
              x[i]['tag'])
