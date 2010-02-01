from google.appengine.ext import db

from models.interestcategory import InterestCategory
from models.application import Application

class ApplicationUser(db.Model):
    user = db.ReferenceProperty(InterestCategory,
                                 required = True,
                                 collection_name = 'region_categories')
    application = db.ReferenceProperty(Application,
                                  required = True,
                                  collection_name = 'region_categories')