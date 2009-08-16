from google.appengine.ext import db

from models.event import *
from models.organization import *

################################################################################
class EventOrganization(db.Model):
  event = db.ReferenceProperty(Event,
                               required = True,
                               collection_name = 'eventorgaizations')
  organization = db.ReferenceProperty(Organization,
                                    required = True,
                                    collection_name = 'eventorganizations')
  