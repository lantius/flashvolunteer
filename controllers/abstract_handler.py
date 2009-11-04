import os
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from controllers._helpers import NeighborhoodHelper
from controllers._utils import is_debugging, get_domain, get_application

from models.volunteer import Volunteer
from models.neighborhood import Neighborhood
from models.event import Event
from models.interestcategory import InterestCategory

from components.sessions import Session

import urllib

################################################################################
# MainPage
class AbstractHandler(webapp.RequestHandler):
    def _get_base_url(self):
        return 'http://www.' + get_domain()
    
    def _add_base_template_values(self, vals):
        session = Session()
        
        vals.update( {
            'domain': self._get_base_url(),
            'path': self.request.path,
            'application_alias': get_application().get_alias(),
            'session_id':  session.sid
        })
        
        volunteer = self.auth()
        if volunteer:
            vals['unread_message_count'] = volunteer.account.get_unread_message_count()
            vals['account'] = volunteer.account
            
            
    def auth(self, requireVolunteer = False, redirectTo = '/login', requireAdmin = False):
        s = Session()
        volunteer = self._auth(requireVolunteer=requireVolunteer, redirectTo = redirectTo, requireAdmin = requireAdmin)
        return volunteer
    
    def _auth(self, requireVolunteer, redirectTo, requireAdmin):
        session = Session()
        #user_object = session.get('user_object', None)
        user_object = None
        if user_object is None:
            auth = session.get('auth', None)
            if requireVolunteer and (not auth or not auth.account):
                req.redirect(redirectTo)
                if redirectTo == '/login': 
                    session['login_redirect'] = req.request.path
                raise AuthError("You must be signed in to perform this action.")
            
            user_object = None
            if auth:
                user_object = Volunteer.all().filter('account =', auth.account).get()
                if not user_object:
                    user_object = Organization.all().filter('account = ', account=account).get()

                application = get_application()
                if not application.key().id() in auth.account.active_applications:
                    auth.account.add_application(application)                      

            if requireVolunteer:
                if self.request.method == 'POST' and not user_object.check_session_id(self.request.get('session_id')):
                    self.redirect('/timeout')
                    raise TimeoutError("Session has timed out.")
                    #return (None)       # shouldn't get here except in tests    
                elif requireAdmin and not users.is_current_user_admin():
                    self.redirect(redirectTo)
                    raise AuthError('You do not have permission to view this page.')
            
            #if user_object: 
            #    session['user_object'] = user_object
        return user_object
        #return session.get('user_object')
      
  
class AuthError(Exception):
    """Exception raised for authorization errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self,message):
        self.message = message
        
class TimeoutError(Exception):
    """Exception raised for timeout errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self,message):
        self.message = message
