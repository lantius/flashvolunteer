from google.appengine.ext import db

################################################################################
# AbstractUser
class AbstractUser(db.Model):
    
    
    #user = db.UserProperty()
    #preferred_email = db.StringProperty(default=None)
    
    name = db.StringProperty()
    avatar = db.BlobProperty()
    avatar_type = db.StringProperty()
    
    quote = db.StringProperty()
    twitter = db.StringProperty()
    joinedon = db.DateProperty(auto_now_add=True)
    
    session_id = db.StringProperty()
    
    verified = db.BooleanProperty(default=False)
    
    applications = db.ListProperty(int)
    
    user = db.UserProperty()
    group_wheel = db.BooleanProperty(default=False) #admin permissions flag

    preferred_email = db.StringProperty(default=None)
    date_added = db.DateProperty(auto_now_add=True)

    error = {}
 
    
    
    def validate(self, params):
        from models.volunteer import Volunteer
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
        if 'delete_avatar' in params:
            self.avatar = None


        if not 'email' in params or not len(params['email']) > 0 or params['email'].find('@') == -1 :
            self.error['email'] = 'A valid email is required'
        else:
            existing_account = Volunteer.all().filter('preferred_email =', params['email']).get()
            if existing_account and existing_account.is_saved():
                self.error['email'] = 'An account with that email already exists. If it is your account, please login in the same way that you created the account.'
            else:
                self.preferred_email  = params['email']
        
        if 'password' in params and params['password'] != params['passwordcheck']:
            self.error['passwords'] = 'Passwords do not match'

        if self.is_saved():
            from models.messages import MessageType, MessagePreference, MessagePropagationType
            
            for message_type in MessageType.all():
                try:
                    message_prefs = self.message_preferences.filter('type =', message_type).get()
                except:
                    message_prefs = None
                    
                if not message_prefs:
                    #### ERROR HERE, can't do volunteer = self
                    #    message_prefs = MessagePreference(type = message_type, propagation = message_type.default_propagation, volunteer = self)
                    # BadValueError: Volunteer instance must have a complete key before it can be stored as a reference
                    message_prefs = MessagePreference(type = message_type, propagation = message_type.default_propagation, user = self)
                    message_prefs.put()
                    
                for mp in MessagePropagationType.all():
                    key = '%s[%s]'%(message_type.key().id(), mp.key().id())
                    if key in params and mp.key().id() not in message_prefs.propagation:
                        message_prefs.propagation.append(mp.key().id())
                        message_prefs.put()
                    elif key not in params and mp.key().id() in message_prefs.propagation:
                        message_prefs.propagation.remove(mp.key().id())
                        message_prefs.put()

            
        return len(self.error) == 0
        
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
           
    def get_messages(self):
        return self.incoming_messages.order('-timestamp')
    
    def get_unread_message_count(self):
        return self.incoming_messages.filter('read =', False).count()

    def get_sent_messages(self):
        return self.sent_messages.order('-trigger')
    
    def get_first_name(self):
        if self.get_name().find('@') > -1:
            return '@'.join(self.get_name().split('@')[:-1])
        else:
            if self.get_name().find(' ') > -1:
                return ' '.join(self.get_name().split(' ')[:-1])
            else: return self.get_name()
            
    def get_last_name(self):
        if self.get_name().find(' ') == -1: return ''
        if self.get_name().find('@') > -1:
            return '@' + self.get_name().split('@')[-1]
        else:
            return self.get_name().split(' ')[-1]
        
    def get_name(self):
        if self.name:
            return self.name
        
        return self.user.nickname()
    
    def get_email(self):
        if self.preferred_email is None:
            return self.user.email()
        else:
            return self.preferred_email
        
    def _get_message_pref(self, type):
        prefs = self.message_preferences.filter('type =', type).get()
        return prefs

    def check_session_id(self, form_session_id, session):
        return form_session_id == session.sid
 
    def is_admin(self):
        return self.group_wheel