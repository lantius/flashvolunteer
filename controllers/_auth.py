from google.appengine.api import users
from models.volunteer import Volunteer
from models.organization import Organization
from components.sessions import Session

import sys, logging

from controllers._utils import get_application

class Authorize():
  
    def login(req, requireVolunteer=False, redirectTo='/login', requireAdmin = False):
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
                user_object = Volunteer.gql("where account = :account", account=auth.account).get()
                if not user_object:
                    user_object = Organization.gql("where account = :account", account=account).get()
                      
            if requireVolunteer:
                if req.request.method == 'POST' and not user_object.check_session_id(req.request.get('session_id')):
                    req.redirect('/timeout')
                    raise TimeoutError("Session has timed out.")
                    #return (None)       # shouldn't get here except in tests    
                elif requireAdmin and not users.is_current_user_admin():
                    req.redirect(redirectTo)
                    raise AuthError('You do not have permission to view this page.')
            
            application = get_application()
            if user_object and not application.key().id() in auth.account.active_applications:
                user_object.add_application(application)
                auth.account.add_application(application)
            
            #if user_object: 
            #    session['user_object'] = user_object
        return user_object
        #return session.get('user_object')
      
    login = staticmethod(login)    
  
  
  
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
