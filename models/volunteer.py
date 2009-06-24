import datetime
from google.appengine.api import users
from google.appengine.ext import db
from models.neighborhood import *
from models.interestcategory import *
from controllers._helpers import SessionID

################################################################################
# Volunteer
class Volunteer(db.Model):
  user = db.UserProperty()
  name = db.StringProperty()
  avatar = db.BlobProperty()
  quote = db.StringProperty()
  twitter = db.StringProperty()
  joinedon = db.DateProperty(auto_now_add=True)
  home_neighborhood = db.ReferenceProperty(Neighborhood, collection_name = 'home_neighborhood')
  work_neighborhood = db.ReferenceProperty(Neighborhood, collection_name = 'work_neighborhood')
  session_id = db.StringProperty()
  create_rights = db.BooleanProperty(default=False)
  preferred_email = db.StringProperty(default=None)
  
  privacy__event_attendance = db.StringProperty(default='friends')

  error = {}


  def validate(self, params):
    self.error.clear()
    
    # volunteer.user is set in the settings controller
    try:
      if not 'name' in params:
        raise Exception
      if not len(params['name']) > 0:        
        raise Exception
      self.name  = params['name']
    except:
      self.error['name'] = ('A name is required', params['name'])
    
    if (not 'tosagree' in params) or params['tosagree'] != '1':
      self.error['tosagree'] = ('You must agree to the Terms of Service to join Flash Volunteer', 0)
    
    if not self.error:
      self.session_id = SessionID().generate()
      return True
    else:
      return False
    
    
    

  def get_name(self):
    if self.name:
      return self.name

    return self.volunteer.nickname

  def get_first_name(self):
      return ' '.join(self.get_name().split(' ')[:-1])
  
  def get_last_name(self):
      return self.get_name().split(' ')[-1]
  
  def get_email(self):
    if self.preferred_email is None:
      return self.user.email()
    else:
      return self.preferred_email
  
  def get_quote(self):
    if self.quote:
      return self.quote
      
    return ''
    
  def url(self):
    return '/volunteers/' + str(self.key().id())

  def logout_url(self):
    return users.create_logout_url('/')

  def events(self):
    return (ev.event for ev in self.eventvolunteers)
  
  def interestcategories(self):
    return (vic.interestcategory for vic in self.volunteerinterestcategories)

  def following(self):
    return (f.volunteer for f in self.volunteerfollowing)

  def following_len(self):
    return len(self.following())

  def followers(self):
    return (f.follower for f in self.volunteerfollowers)

  def followers_len(self):
    return len(self.followers())

  # both following and follower
  def friends(self):
    fr = []
    for following in self.following():
      for follower in self.followers():
        if following.key().id() == follower.key().id():
          fr.append(following)
    return (f for f in fr)

  def friends_len(self):
    return len(self.friends())

  def followers_only(self):
      friends = dict([(f.key().id(),1) for f in self.friends()])
      return (f for f in self.followers() if f.key().id() not in friends)

  def following_only(self):
      friends = dict([(f.key().id(),1) for f in self.friends()])
      return (f for f in self.following() if f.key().id() not in friends)

  def events_past_count(self):
    return len(self.events_past())

  def events_past(self):
    return [e for e in self.events() if e.date < datetime.datetime.today() ]
  
  def events_future_count(self):
    return len(self.events_future())

  def events_future(self):
    return [e for e in self.events() if e.date >= datetime.datetime.today() ]
  
  def check_session_id(self, form_session_id):
    return form_session_id == self.session_id
    
  def can_create_events(self):
    return self.create_rights

  def event_access(self, volunteer):
      friends = [f.key().id() for f in self.friends()]
      return self.privacy__event_attendance == 'everyone' or (self.privacy__event_attendance == 'friends' and volunteer.key().id() in friends)
      
  
