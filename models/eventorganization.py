from google.appengine.ext import db

from models.event import Event
from models.organization import Organization

################################################################################
class EventOrganization(db.Model):
    event = db.ReferenceProperty(Event,
                                 required = True,
                                 collection_name = 'eventorganizations')
    organization = db.ReferenceProperty(Organization,
                                      required = True,
                                      collection_name = 'eventorganizations')
