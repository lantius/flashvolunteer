############ DEPRECATED

from google.appengine.ext import db

from models.volunteer import Volunteer
from models.interestcategory import InterestCategory

class VolunteerInterestCategory(db.Model):
    volunteer = db.ReferenceProperty(Volunteer,
                                 required = True,
                                 collection_name = 'volunteerinterestcategories')
    interestcategory = db.ReferenceProperty(InterestCategory,
                                  required = True,
                                  collection_name = 'volunteerinterestcategories')
