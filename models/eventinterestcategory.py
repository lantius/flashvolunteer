from google.appengine.ext import db

from models.event import Event
from models.interestcategory import InterestCategory

class EventInterestCategory(db.Model):
    event = db.ReferenceProperty(Event,
                                 required = True,
                                 collection_name = 'event_categories')
    interestcategory = db.ReferenceProperty(InterestCategory,
                                  required = True,
                                  collection_name = 'event_categories')
    
    ### These are shadow properties of Event, that would ideally be accessed there,
    ### but which cannot be during datastore queries, as that would use an implicit
    ### join. Would love to eliminate these if someone has a good idea...
    event_is_upcoming = db.BooleanProperty(default = True)
    event_is_hidden = db.BooleanProperty(default = False)
    event_date = db.DateTimeProperty()