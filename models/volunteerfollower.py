from google.appengine.ext import db

from models.volunteer import Volunteer

from models.auth.account import Account

class VolunteerFollower(db.Model):
  volunteer = db.ReferenceProperty(Volunteer,
                                   #required = True,
                                   collection_name = 'volunteerfollowers')
  follower = db.ReferenceProperty(Volunteer,
                                  #required = True,
                                  collection_name = 'volunteerfollowing')

  follows = db.ReferenceProperty(Account,
                                 collection_name = 'followers')
  follower2 = db.ReferenceProperty(Account,
                                  collection_name = 'following')