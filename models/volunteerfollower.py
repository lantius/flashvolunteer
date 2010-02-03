from google.appengine.ext import db

from models.auth.account import Account

class VolunteerFollower(db.Model):
    follower = db.ReferenceProperty(reference_class = None,
                                    required = True,
                                    collection_name = 'following')
    
    follows = db.ReferenceProperty(Account,
                                   collection_name = 'followers')
    
    mutual = db.BooleanProperty(default = False)
    
    date_added = db.DateProperty(auto_now_add=True)