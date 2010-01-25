import datetime
import logging
import urllib
from components.geostring import *
from components.time_zones import Pacific

from components.time_zones import now

from google.appengine.api import urlfetch

from google.appengine.ext import db

################################################################################
# RegionDomain
class Application(db.Model):
    name = db.StringProperty()
    ne_coord = db.GeoPtProperty() # No default
    sw_coord = db.GeoPtProperty()
    
    def get_alias(self):
        return self.name.replace('-', ' ').title()

  
    def upcoming_events(self, date = None):
        if date is None: date = now()
                
        events = self.events.filter(
            'date >= ', date).filter(
            'hidden = ', False).order(
            'date')
        
        return events