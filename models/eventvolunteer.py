from google.appengine.ext import db

from models.event import Event

from models.volunteer import Volunteer
from models.auth.account import Account


################################################################################
class EventVolunteer(db.Model):
  event = db.ReferenceProperty(Event,
                               required = True,
                               collection_name = 'eventvolunteers')
  
  volunteer = db.ReferenceProperty(Volunteer,
         #                           required = True,
                                    collection_name = 'eventvolunteers')

  account = db.ReferenceProperty(Account,
                                    #required = True,
                                    collection_name = 'eventvolunteers')
    
  isowner = db.BooleanProperty(required = True)
  attended = db.BooleanProperty(default = None)
  hours = db.IntegerProperty()
  