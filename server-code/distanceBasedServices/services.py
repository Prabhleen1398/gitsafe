#from django.http import JsonResponse
from django.http import HttpResponse

import pandas as pd
import numpy as np

def services(request):
    lat = float(request.GET.get('lat',''))
    lng = float(request.GET.get('lng',''))
    name = request.GET.get('name','')
    
    
    import pyrebase 
    config = { 
        "apiKey": "INSERT_API_KEY",
        "authDomain": "smartpune-b614c.firebaseapp.com",
        "databaseURL": "https://smartpune-b614c.firebaseio.com",
        "projectId": "smartpune-b614c",
        "storageBucket": "smartpune-b614c.appspot.com",
        "messagingSenderId": "INSERT_MESSAGING_SENDER_ID"
    }

    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    auth.sign_in_with_email_and_password('backend1@smartpune.com','firebase')
    
    db = firebase.database()
    ambulancesData = db.child("data").child("services").child("ambulances").get()
    
    df = pd.DataFrame(ambulancesData.val()).transpose()
    
    df = df[df.status == 'free']
    
    if df.shape[0] > 0:
        df["keys"] = df.index

        df.set_index(np.arange(0,df.shape[0]),inplace=True)


        for i in range(0,df.shape[0]):
            df.loc[i,"distance"] = distanceFrom(df.loc[i,"lat"], df.loc[i,"lng"], lat, lng)

        df2 = df[df.distance == df.distance.min()]
        key = df2["keys"].values[0]
        df2.drop(["keys"],axis=1,inplace=True)
        daa = ((df2.T).to_dict()).popitem()[1]


        daa["status"] = "busy"
        del(daa["distance"])
        daa["job"] = {
                "lat" : lat,
                "lng" : lng,
                "name" : name
        }

        db = firebase.database()
        ambulances = db.child("data").child("services").child("ambulances")
        ambulances.child(key).update(daa)
    else:
        key = "0"

    #return JsonResponse({"key": key})
    return HttpResponse(key)
    

def distanceFrom(lat1, lng1, lat2, lng2):
    from math import sin, cos, sqrt, atan2, radians
    R = 6373.0
    lat1 = radians(lat1)
    lon1 = radians(lng1)
    lat2 = radians(lat2)
    lon2 = radians(lng2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance