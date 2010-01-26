import os,datetime, logging, urllib
from google.appengine.api import urlfetch
from components.geostring import Geostring
from google.appengine.ext import db


def geocode(address):
    response = urlfetch.fetch('http://maps.google.com/maps/geo?q=' + urllib.quote_plus(address) + '&output=csv&oe=utf8&sensor=false&key=' + get_google_maps_api_key())
    (httpcode) = response.content.split(',')[0]
    if '200' == httpcode:
        (httpcode, accuracy, lat, lon) = response.content.split(',')
        location = db.GeoPt(lat, lon)
        return (location, str(Geostring((location.lat, location.lon))))
    else:
        raise Exception('Could not geocode that location')

def get_neighborhood(application, address):
    
    if len(address.split(' ')) < 5:
        #just a hack to cull out those that definitely aren't complete addresses    
        return None  
        
    (location, geostring) = geocode(address)
    
    distances = [(n.distance_from_centroid(location), n) for n in application.neighborhoods if n.centroid and n.centroid.lat]
    distances.sort(lambda a,b:int(a[0]*1000-b[0]*1000))

    return distances[-1]

def get_google_maps_api_key():
#    if server == 0:
#        return 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBT8o8BW0NprhG7ZQBw6sHycsndbhRS7hhGpRgOy2Kssletcr3BQkAy7jg'
#    elif server == 1:
#        if os.environ['HTTP_HOST'].find('appspot.com') > -1:
#            return 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBRzNuM6YWShM3q9_tmx1xqncfIVVBTbiYMhS-lVDJ8Xb4gcYINCK_rBMA'
#
#        else: 
#            return 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBSQPgw8JI6IbILJlYJvqzvWY-lLQBTXCrJQnsm-dzTVGDCeBq80bPNwUQ'
#    else:
#        if os.environ['HTTP_HOST'].find('appspot.com') > -1: 
#            return 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBQ_mWzt9DEjH1LJGfRCLKaKtSAdHRQWpcGvL4nHZQAotfUyiCJ_18AvbQ'
#        else:
            return 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBSQPgw8JI6IbILJlYJvqzvWY-lLQBTXCrJQnsm-dzTVGDCeBq80bPNwUQ'
