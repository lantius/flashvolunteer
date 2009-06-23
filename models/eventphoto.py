from google.appengine.ext import db

from models.event import *
from models.volunteer import *

################################################################################
class EventPhoto(db.Model):
  event = db.ReferenceProperty(Event,
                               required = True,
                               collection_name = 'eventphotos')
  
  #person who posted photo or created album
  volunteer = db.ReferenceProperty(Volunteer,
                                    required = True,
                                    collection_name = 'eventphotos')
  
  #link, or title for INTERNAL_ALBUM)
  content = db.StringProperty(required = True)
  
  type = db.IntegerProperty(required = True)
  #type values
  RSS_ALBUM=1
  INTERNAL_ALBUM=2
  #FACEBOOK_ALBUM=3
  PHOTO=4

  status = db.IntegerProperty(required = True)
  #status values
  UNPUBLISHED=1
  PUBLISHED=2

  #determines order of display, smaller numbers first
  display_weight = db.IntegerProperty(default = 0)
  
  #None for root; parent should only be INTERNAL_ALBUM
  display_parent = db.SelfReferenceProperty(default = None,
                                            collection_name = 'eventphotoparents') 
