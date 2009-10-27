from controllers._utils import get_google_maps_api_key, get_application
from google.appengine.api import urlfetch
from google.appengine.ext import db
import datetime, logging, urllib

################################################################################
# Event
class Account(db.Model):
    user = db.UserProperty()
    name = db.StringProperty()    

    preferred_email = db.StringProperty(default=None)
    active_applications = db.ListProperty(int)

    error = {}

    def add_application(self, application):
        self.active_applications.append(application.key().id())
        self.put()
        
    def validate(self, params):
        self.error.clear()
        
        if not 'name' in params or len(params['name']) < 1:
            self.error['name'] = ('A name is required', params['name'])
        else:
            self.name  = params['name']
        
        if not self.is_saved():
            if (not 'tosagree' in params) or params['tosagree'] != '1':
                self.error['tosagree'] = ('You must agree to the Terms of Service to join Flash Volunteer', 0)
                  
        if not 'email' in params or not len(params['email']) > 0 or params['email'].find('@') == -1 :
            self.error['email'] = ('A valid email is required', params['email'])
        else:
            existing_account = Account.all().filter('preferred_email =', params['email']).get()
            if existing_account and existing_account.is_saved():
                self.error['email'] = ('An account using that email already exists', params['email'])
            else:
                self.preferred_email  = params['email']
        
        if 'password' in params and params['password'] != params['passwordcheck']:
            self.error['passwords'] = ('Passwords do not match',)
            
        return len(self.error) == 0