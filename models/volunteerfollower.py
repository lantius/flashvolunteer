from google.appengine.ext import db

from models.volunteer import Volunteer

from models.auth.account import Account

class VolunteerFollower(db.Model):
    ##### DEPRECATED
    volunteer = db.ReferenceProperty(Volunteer,
                                     #required = True,
                                     collection_name = 'volunteerfollowers')
    ##############
    
    follower = db.ReferenceProperty(reference_class = None,
                                    #required = True,
                                    collection_name = 'following')
    
    follows = db.ReferenceProperty(Account,
                                   collection_name = 'followers')