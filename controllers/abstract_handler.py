import os
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from controllers._utils import is_debugging, get_domain, get_application

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
        
        account = self.auth()
        if account:
            vals['unread_message_count'] = account.get_unread_message_count()
            vals['account'] = account
            
            
    def auth(self, require_login = False, redirect_to = '/login', require_admin = False):
        s = Session()
        account = self._auth(require_login=require_login, redirect_to = redirect_to, require_admin = require_admin)
        
        return account
    
    def _auth(self, require_login, redirect_to, require_admin):
        session = Session()
        auth = session.get('auth', None)
        if require_login and (not auth or not auth.account):
            self.redirect(redirect_to)
            if redirect_to == '/login': 
                session['login_redirect'] = self.request.path
            raise AuthError("You must be signed in to perform this action.")
        
        if auth:
            application = get_application()
            if not application.key().id() in auth.account.active_applications:
                auth.account.add_application(application)                      

        if require_login:
            if self.request.method == 'POST' and not auth.account.check_session_id(self.request.get('session_id')):
                self.redirect('/timeout')
                raise TimeoutError("Session has timed out.")
                #return (None)       # shouldn't get here except in tests    
            elif require_admin and not users.is_current_user_admin():
                self.redirect(redirect_to)
                raise AuthError('You do not have permission to view this page.')
            
        if not auth:
            return None
        
        return auth.account
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
