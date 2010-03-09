from utils.applications.defs._application_def import ApplicationDef
from google.appengine.ext import db

############################
class GeorgeTown(ApplicationDef):
    ne_coord = db.GeoPt(lat = 47.834116 , lon = -122.066345 )
    sw_coord = db.GeoPt(lat = 47.434343 , lon = -122.567596 )
    
    def get_name(self):
        return 'georgetown'
    
    def get_subdomains(self):
        return ['']
    
    def get_neighborhoods(self):
        return (
                ('GW1', 47.683997, -122.381086),
                ('GW2', 47.588626,-122.309246),
                ('GW3', 47.624562, -122.345552),
                ('GW4', 47.632429, -122.312078),
                )
