############ DEPRECATED

from google.appengine.ext import db

from models.volunteer import *
from models.interestcategory import *

class VolunteerInterestCategory(db.Model):
    volunteer = db.ReferenceProperty(Volunteer,
                                 required = True,
                                 collection_name = 'volunteerinterestcategories')
    interestcategory = db.ReferenceProperty(InterestCategory,
                                  required = True,
                                  collection_name = 'volunteerinterestcategories')
