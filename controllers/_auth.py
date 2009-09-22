from google.appengine.api import users
from models.volunteer import Volunteer
from models.organization import Organization
from components.sessions import Session

import sys

class Authorize():
  
  def login(req, requireVolunteer=False, redirectTo=''):
    session = Session()
    user = session.get('user', None)
    
    abstract_user = None
    
    if user:
      abstract_user = Volunteer.gql("where user = :user", user=user).get()
      if not abstract_user:
          abstract_user = Organization.gql("where user = :user", user=user).get()
              
    if requireVolunteer:
      if not abstract_user:
        req.redirect(redirectTo)
        raise AuthError("You must be signed in to perform this action.")
        #sys.exit(0)           # should end execution IRL
        #return (None)      # shouldn't get here except in tests
        
      elif req.request.method == 'POST' and not abstract_user.check_session_id(req.request.get('session_id')):
        req.redirect('/timeout')
        raise TimeoutError("Session has timed out.")
        #return (None)       # shouldn't get here except in tests    
    
    return abstract_user
    
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
