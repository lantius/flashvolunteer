from google.appengine.ext import db

from models.event import Event

from models.volunteer import Volunteer
from models.auth.account import Account
from models.application import Application

################################################################################
class EventVolunteer(db.Model):
    event = db.ReferenceProperty(Event,
                                 required = True,
                                 collection_name = 'eventvolunteers')
    
    volunteer = db.ReferenceProperty(Volunteer,
                                      required = True,
                                      collection_name = 'eventvolunteers')
    
    isowner = db.BooleanProperty(required = True)
    attended = db.BooleanProperty(default = None)
    hours = db.IntegerProperty()
    interest_level = db.IntegerProperty(default=2)
    
    ### These are shadow properties of Event, that would ideally be accessed there,
    ### but which cannot be during datastore queries, as that would use an implicit
    ### join. Would love to eliminate these if someone has a good idea...
    event_is_upcoming = db.BooleanProperty(default = True)
    event_is_hidden = db.BooleanProperty(default = False)
    event_date = db.DateTimeProperty()
    application = db.ReferenceProperty(Application, collection_name = 'eventvolunteers')