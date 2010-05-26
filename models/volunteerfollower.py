from google.appengine.ext import db

from models.volunteer import Volunteer

class VolunteerFollower(db.Model):
    follower = db.ReferenceProperty(reference_class = None,
                                    required = True,
                                    collection_name = 'following')
   
    followed = db.ReferenceProperty(Volunteer,
                                   collection_name = 'followers')
    
    mutual = db.BooleanProperty(default = False)
    
    date_added = db.DateProperty(auto_now_add=True)