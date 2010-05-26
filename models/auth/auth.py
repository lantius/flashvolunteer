from google.appengine.api import urlfetch
from google.appengine.ext import db
import datetime, logging, urllib

from models.volunteer import Volunteer

################################################################################
# Event
class Auth(db.Model):
    strategy = db.StringProperty(required = True)
    identifier = db.StringProperty(required = True)
    digest = db.StringProperty()
    digest2 = db.StringProperty()
    salt = db.StringProperty()
    user = db.ReferenceProperty(Volunteer, collection_name = 'auth_methods')
    
