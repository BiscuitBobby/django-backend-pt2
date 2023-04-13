import geohash
from firebase_admin import firestore, credentials, initialize_app
from uuid import uuid4

cred = credentials.Certificate("Backend_pt2_app/admin-sdk.json")
__all__ = ['send_to_firebase', 'update_firebase_snapshot']
initialize_app(cred)

def send_to_firebase(user=str(uuid4()), location=None, active=False):
    if location is None:
        location = [0, 0]
    db = firestore.client()
    data = {'user': user}
    
    locations_ref = db.collection('data')
    query = locations_ref.where('user', '==', user)
    docs = query.get()
    if len(docs) < 1:
        db.collection('data').document(user).create(data)
    update_firebase_snapshot(location, user, 'password', active)
    return 0


def update_firebase_snapshot(location,
                             user='test1',
                             pswrd='password',
                             active=True,
                             event_name=None,
                             event_description=None,
                             event_type='food'):
    db = firestore.client()
    geopoint = firestore.GeoPoint(*location)

    # Encode the geopoint with geohash
    geohash_str = geohash.encode(*location)

    locations_ref = db.collection('data')

    query = locations_ref.where('user', '==', user)
    docs = query.get()
    if active == False:  # delete document if false
        doc_ref = db.collection('geopoints').document(user)
        doc_ref.delete()
        print(f"deleted {user}'s event")
    else:
        for doc in docs:
            print(f'Document ID: {doc.id}')
            print(f'pass: {doc.to_dict()["password"]}')

        if pswrd == doc.to_dict()["password"]:
            # Add the geopoint to Firestore
            doc_ref = db.collection('geopoints').document(user)
            doc_ref.set({
                'name': user,
                'geopoint': geopoint,
                'geohash': geohash_str,
                'active': active,
                'event_name': event_name,
                'event_description': event_description,
                'tag': event_type
            })
    return 0
