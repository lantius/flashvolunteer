from google.appengine.api import users
from models.volunteer import Volunteer
from components.sessions import Session

import sys

class Authorize():
  
  def login(req, requireVolunteer=False, redirectTo=''):
    session = Session()
    user = session.get('user', None)
    
    if user:
      volunteer = Volunteer.gql("where user = :user", user=user).get()
    else:
      volunteer = None
              
    if requireVolunteer:
      if not volunteer:
        req.redirect(redirectTo)
        raise AuthError("You must be signed in to perform this action.")
        #sys.exit(0)           # should end execution IRL
        #return (None)      # shouldn't get here except in tests
        
      elif req.request.method == 'POST' and not volunteer.check_session_id(req.request.get('session_id')):
        req.redirect('/timeout')
        raise TimeoutError("Session has timed out.")
        #return (None)       # shouldn't get here except in tests    
    
    return volunteer
    
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
