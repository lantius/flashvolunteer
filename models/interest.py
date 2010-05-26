from google.appengine.ext import db

from models.volunteer import Volunteer
from models.interestcategory import InterestCategory

class Interest(db.Model):
    user = db.ReferenceProperty(Volunteer,
                                collection_name = 'user_interests')

    interestcategory = db.ReferenceProperty(InterestCategory,
                                required = True,
                                collection_name = 'user_interests')
    
    date_added = db.DateProperty(auto_now_add=True)