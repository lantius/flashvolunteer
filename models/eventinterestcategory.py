from google.appengine.ext import db

from models.event import Event
from models.interestcategory import InterestCategory

class EventInterestCategory(db.Model):
  event = db.ReferenceProperty(Event,
                               required = True,
                               collection_name = 'eventinterestcategories')
  interestcategory = db.ReferenceProperty(InterestCategory,
                                required = True,
                                collection_name = 'eventinterestcategories')