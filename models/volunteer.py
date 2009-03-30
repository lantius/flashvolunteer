import datetime
from google.appengine.ext import db
from models.neighborhood import *
from models.interestcategory import *

################################################################################
# Volunteer
class Volunteer(db.Model):
  user = db.UserProperty()
  name = db.StringProperty()
  avatar = db.BlobProperty()
  quote = db.StringProperty()
  joinedon = db.DateProperty(auto_now_add=True)
  home_neighborhood = db.ReferenceProperty(Neighborhood, collection_name = 'home_neighborhood')
  work_neighborhood = db.ReferenceProperty(Neighborhood, collection_name = 'work_neighborhood')
  session_id = db.StringProperty()

  def get_name(self):
    if self.name:
      return self.name

    return self.user.nickname
    
  def url(self):
    return '/volunteers/' + str(self.key().id())

  def events(self):
    return (ev.event for ev in self.eventvolunteers)
  
  def interestcategories(self):
    return (vic.interestcategory for vic in self.volunteerinterestcategories)

  def following(self):
    return (f.volunteer for f in self.volunteerfollowing)

  def followers(self):
    return (f.follower for f in self.volunteerfollowers)

  def events_past_count(self):
    return len(self.events_past())

  def events_past(self):
    future_filter = lambda x: x.date < datetime.datetime.today()
    return filter(future_filter, self.events())
  
  def events_future_count(self):
    return len(self.events_future())

  def events_future(self):
    future_filter = lambda x: x.date >= datetime.datetime.today()
    return filter(future_filter, self.events())
        
  # both following and follower
  def friends(self):
    fr = []
    for following in self.following():
      for follower in self.followers():
        if following.key().id() == follower.key().id():
          fr.append(following)
    return (f for f in fr)

  def check_session_id(self, form_session_id):
    if form_session_id == self.session_id:
      return True
    
    return False