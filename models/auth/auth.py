from controllers._utils import get_google_maps_api_key, get_application
from google.appengine.api import urlfetch
from google.appengine.ext import db
import datetime, logging, urllib

from models.auth import Account
################################################################################
# Event
class Auth(db.Model):
    strategy = db.StringProperty(required = True)
    identifier = db.StringProperty(required = True)
    digest = db.StringProperty()
    digest2 = db.StringProperty()
    salt = db.StringProperty()
    account = db.ReferenceProperty(Account,
                                   collection_name='auth_methods')
    
    