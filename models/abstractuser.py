from google.appengine.ext import db
from models.neighborhood import Neighborhood
from models.application import Application
from models.auth import Account

#For verifying volunteer creation
from controllers._twitter import Twitter 

from components.sessions import Session

################################################################################
# AbstractUser
class AbstractUser(db.Model):
    user = db.UserProperty()
    name = db.StringProperty()
    avatar = db.BlobProperty()
    avatar_type = db.StringProperty()
    
    quote = db.StringProperty()
    twitter = db.StringProperty()
    joinedon = db.DateProperty(auto_now_add=True)
    
    session_id = db.StringProperty()
    preferred_email = db.StringProperty(default=None)
    
    verified = db.BooleanProperty(default=False)
    
    applications = db.ListProperty(int)
    
    error = {}
    
    account = db.ReferenceProperty(Account)
    
    
    def validate(self, params):
      self.error.clear()
      
      # AbstractUser.user is set in the settings controller
      
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
      raise Exception("extend url function")
    
    def logout_url(self):
      return '/logout'
    
    def events(self):
      events = [ev.event for ev in self.eventvolunteers.filter('isowner =',False) if not ev.event.hidden]
      events.sort(cmp = lambda e,e2: cmp(e.date,e2.date))
      return events
    
    def events_coordinating(self):
      events = [ev.event for ev in self.eventvolunteers.filter('isowner =',True) if not ev.event.inpast() and not ev.event.hidden]
      events.sort(cmp = lambda e,e2: cmp(e.date,e2.date))
      return events
    
    def interestcategories(self):
      return (vic.interestcategory for vic in self.volunteerinterestcategories)
    
    def events_past_count(self):
      return len(self.events_past())
    
    def events_past(self):
      return [e for e in self.events() if e.inpast() and not e.hidden]
    
    def events_future_count(self):
      return len(self.events_future())
    
    def events_future(self):
      return [e for e in self.events() if not e.inpast() and not e.hidden]
    
    def check_session_id(self, form_session_id):
      session = Session()
      return form_session_id == session.sid
    
    def add_application(self, application):
        self.applications.append(application.key().id())
        self.put()
      
