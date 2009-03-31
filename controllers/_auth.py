from google.appengine.api import users
from models.volunteer import *
import sys

class Authorize():
  
  def login(req, requireVolunteer=False, redirectTo=''):
    user = users.get_current_user()
    
    if user:
      volunteer = Volunteer.gql("where user = :user", user=user).get()
    else:
      volunteer = None
    
    if requireVolunteer:
      
      if not volunteer:
        req.redirect(redirectTo)
        sys.exit            # should end execution IRL
        return (None) # shouldn't get here except in tests
        
      if volunteer and req.request.method == 'POST' and not volunteer.check_session_id(req.request.get('session_id')):
        req.redirect('/timeout')
        sys.exit            # should end execution IRL
        return (None) # shouldn't get here except in tests    
    
    return(volunteer)
  
  login = staticmethod(login)