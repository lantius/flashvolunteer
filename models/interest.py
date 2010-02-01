from google.appengine.ext import db

from models.auth.account import Account
from models.interestcategory import InterestCategory

class Interest(db.Model):
    account = db.ReferenceProperty(Account,
                               required = True,
                               collection_name = 'user_interests')
  
    interestcategory = db.ReferenceProperty(InterestCategory,
                                required = True,
                                collection_name = 'user_interests')
