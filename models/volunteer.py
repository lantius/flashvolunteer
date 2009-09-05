from google.appengine.ext import db
from models.neighborhood import Neighborhood

#For verifying volunteer creation
from controllers._twitter import Twitter 


################################################################################
# Volunteer
class Volunteer(db.Model):
  user = db.UserProperty()
  name = db.StringProperty()
  avatar = db.BlobProperty()
  avatar_type = db.StringProperty()
  
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
    
    if not self.is_saved():
      if (not 'tosagree' in params) or params['tosagree'] != '1':
        self.error['tosagree'] = ('You must agree to the Terms of Service to join Flash Volunteer', 0)
   
    # Not verifying these updates
    if 'home_neighborhood' in params:
      if params['home_neighborhood'] == 'None':
        self.home_neighborhood = None;
      else:
        self.home_neighborhood = Neighborhood.get_by_id(int(params['home_neighborhood']))

    if 'work_neighborhood' in params:
      if params['work_neighborhood'] == 'None':
        self.work_neighborhood = None;
      else:
        self.work_neighborhood = Neighborhood.get_by_id(int(params['work_neighborhood']))

    if 'quote' in params:
      self.quote = "" + params['quote']
    if 'name' in params:
      self.name  = params['name']
    if 'delete_avatar' in params:
      self.avatar = None
      
    try:
      if not 'email' in params or not len(params['email']) > 0 or params['email'].find('@') == -1 :
        raise Exception
      self.preferred_email  = params['email']
    except:
      self.error['email'] = ('A valid email is required', params['email'])
      
    if 'twitter' in params and self.twitter != params['twitter']:
      self.twitter = params['twitter']
      Twitter.toot("Welcome to Flash Volunteer!", self.twitter)

      #Interest Categories updates happen in the controller

    if 'privacy__event_attendance' in params and self.privacy__event_attendance != params['privacy__event_attendance']:
        self.privacy__event_attendance = params['privacy__event_attendance']
    
    
    if not self.error:
      from controllers._helpers import SessionID
      self.session_id = SessionID().generate()
      return True
    else:
      return False


  def get_name(self):
    if self.name:
      return self.name

    return self.volunteer.nickname

  def get_first_name(self):
      if self.get_name().find('@') > -1:
          return '@'.join(self.get_name().split('@')[:-1])
      else:
          return ' '.join(self.get_name().split(' ')[:-1])
  
  def get_last_name(self):
      if self.get_name().find('@') > -1:
          return '@' + self.get_name().split('@')[-1]
      else:
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
    return '/logout'

  def events(self):
    events = [ev.event for ev in self.eventvolunteers if not ev.event.hidden]
    events.sort(cmp = lambda e,e2: cmp(e.date,e2.date))
    return events

  def events_coordinating(self):
    events = [ev.event for ev in self.eventvolunteers if ev.isowner and not ev.event.inpast() and not ev.event.hidden]
    events.sort(cmp = lambda e,e2: cmp(e.date,e2.date))
    return events      

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

  def teammates_ids(self):
      return dict([(v.key().id(),1) for v in self.following() ])

  # both following and follower
  def friends(self):
    fr = []
    
    following = dict([(f.key().id(),1) for f in self.following()])
    for follower in self.followers():
        if follower.key().id() in following:            
          fr.append(follower)
    return [f for f in fr]

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
    return [e for e in self.events() if e.inpast() and not e.hidden]
  
  def events_future_count(self):
    return len(self.events_future())

  def events_future(self):
    return [e for e in self.events() if not e.inpast() and not e.hidden]
  
  def check_session_id(self, form_session_id):
    return form_session_id == self.session_id
    
  def can_create_events(self):
    return self.create_rights

  def event_access(self, volunteer):
      friends = [f.key().id() for f in self.friends()]
      return self.privacy__event_attendance == 'everyone' or (self.privacy__event_attendance == 'friends' and volunteer.key().id() in friends)
      
  
