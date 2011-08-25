from google.appengine.api import urlfetch
from google.appengine.ext import db
from models.event import Event
import datetime, logging, urllib

class NewCheckin(db.Model):
    name = db.StringProperty(required = True)
    email = db.StringProperty(required = True)
    event = db.ReferenceProperty(Event,
                                 required = True,
                                 collection_name = 'checked_in')
    
    def __init__(self, ame, mail, vent):
        db.Model.__init__(self, name=ame, email=mail, event=vent)
