from google.appengine.ext import db

from models.volunteer import *
from models.organization import *

class OrganizationFollower(db.Model):
  organization = db.ReferenceProperty(Organization,
                                   required = True,
                                   collection_name = 'organizationfollowers')
  follower = db.ReferenceProperty(Volunteer,
                                  required = True,
                                  collection_name = 'organizationfollowing')
                                  
