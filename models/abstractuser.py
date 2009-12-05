from google.appengine.ext import db
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
    
    def get_quote(self):
        if self.quote:
            return self.quote
        
        return ''
      
    def url(self):
        raise Exception("extend url function")

    def events(self):
        return self.eventvolunteers.filter('isowner =',False).filter('event_is_hidden =', False).order('event_date')
    
    def events_coordinating(self):
        return self.eventvolunteers.filter('isowner =',True).filter('event_is_upcoming =',True).filter('event_is_hidden =', False).order('event_date')
    
    def past_events_coordinated(self):
        return self.eventvolunteers.filter('isowner =',True).filter('event_is_upcoming =',False).filter('event_is_hidden =', False).order('event_date')

    def interestcategories(self):
        return (vic.interestcategory for vic in self.user_interests)
    
    def events_past_count(self):
        return self.events_past().count()
    
    def events_past(self):
        return self.eventvolunteers.filter('isowner =',False).filter('event_is_upcoming =',False).filter('event_is_hidden =', False).order('event_date')
    
    def events_future_count(self):
        return self.events_future().count()
    
    def events_future(self):
        return self.eventvolunteers.filter('isowner =',False).filter('event_is_upcoming =',True).filter('event_is_hidden =', False).order('event_date')
    
    def add_application(self, application):
        self.applications.append(application.key().id())
        self.put()
      
    def get_activities(self, limit = None):
        if limit:     
            future_events = [ev.event for ev in self.events_future().fetch(limit)]
            past_events = [ev.event for ev in self.events_past().fetch(limit)]     
            events_coordinating = [ev.event for ev in self.events_coordinating().fetch(limit)]
            past_events_coordinated = [ev.event for ev in self.past_events_coordinated().fetch(limit)]
        else:
            future_events = self.events_future().count()
            past_events = self.events_past().count()     
            events_coordinating = self.events_coordinating().count()
            past_events_coordinated = self.past_events_coordinated().count()
            
        
        return (future_events, past_events, events_coordinating, past_events_coordinated)