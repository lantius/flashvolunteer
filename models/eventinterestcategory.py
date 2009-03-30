from google.appengine.ext import db

from models.event import *
from models.interestcategory import *

class EventInterestCategory(db.Model):
  event = db.ReferenceProperty(Event,
                               required = True,
                               collection_name = 'eventinterestcategories')
  interestcategory = db.ReferenceProperty(InterestCategory,
                                required = True,
                                collection_name = 'eventinterestcategories')