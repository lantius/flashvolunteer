from google.appengine.ext import db

from models.volunteer import *

class VolunteerFollower(db.Model):
  volunteer = db.ReferenceProperty(Volunteer,
                                   required = True,
                                   collection_name = 'volunteerfollowers')
  follower = db.ReferenceProperty(Volunteer,
                                  required = True,
                                  collection_name = 'volunteerfollowing')
                                  


