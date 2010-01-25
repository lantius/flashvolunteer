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
    
    distances = [(n.distance_from_centroid(location), n) for n in application.neighborhoods]
    distances.sort(lambda a,b:int(a[0]*1000-b[0]*1000))

    return distances[-1]