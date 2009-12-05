from google.appengine.ext import db
import datetime, logging, urllib
from components.sessions import Session

################################################################################
# Event
class Account(db.Model):
    user = db.UserProperty()
    name = db.StringProperty()    
    group_wheel = db.BooleanProperty() #admin permissions flag

    preferred_email = db.StringProperty(default=None)
    active_applications = db.ListProperty(int)

    error = {}

    def add_application(self, application):
        self.active_applications.append(application.key().id())
        self.put()
        
    def validate(self, params):
        self.error.clear()
        
        if not 'name' in params or len(params['name']) < 1:
            self.error['name'] = 'A name is required'
        else:
            self.name  = params['name']
        
        if not self.is_saved():
            if (not 'tosagree' in params) or params['tosagree'] != '1':
                self.error['tosagree'] = 'You must agree to the Terms of Service to join Flash Volunteer'
                  
        if not 'email' in params or not len(params['email']) > 0 or params['email'].find('@') == -1 :
            self.error['email'] = 'A valid email is required'
        else:
            existing_account = Account.all().filter('preferred_email =', params['email']).get()
            if existing_account and existing_account.is_saved():
                self.error['email'] = 'An account using that email already exists'
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
                    message_prefs = MessagePreference(type = message_type, propagation = message_type.default_propagation, account = self)
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
    
    def get_user(self):
        if self.vol_user:
            return self.vol_user.get()
        elif self.org_user:
            return self.org_user.get()
        
        
    def get_messages(self):
        return self.incoming_messages.order('-timestamp')
    
    def get_unread_message_count(self):
        return self.incoming_messages.filter('read =', False).count()

    def get_sent_messages(self):
        return self.sent_messages.order('-trigger')
    
    def is_recipient(self, message):
        from models.messages import MessageReceipt
        mr = MessageReceipt.filter('recipient =', self.account)
        return mr.get() is not None
    
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

    def check_session_id(self, form_session_id):
        session = Session()
        return form_session_id == session.sid
 
 
    def url(self):
        return self.get_user().url()
  
    def avatar(self):
        return self.get_user().avatar

    def is_admin(self):
#TODO: make sure this test is valid...
        return self.group_wheel
  
