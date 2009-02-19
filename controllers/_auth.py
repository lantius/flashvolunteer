from google.appengine.api import users
from models import Volunteer
import sys

class Authorize():
  
  def login(req, requireUser=False, requireVolunteer=False, redirectTo=''):
    user = users.get_current_user()
    
    if requireUser and not user:
      req.redirect(users.create_login_url(req.request.uri))
      sys.exit
    
    if user:
      volunteer = Volunteer.gql("where user = :user", user=user).get()
      
    if requireVolunteer:
      
      if not volunteer:
        req.redirect(redirectTo)
        raise NoVolunteerError, "No volunteer for the user"

        volunteer = volunteers.get()

      if volunteer and req.request.method == 'POST' and not volunteer.check_session_id(req.request.get('session_id')):
        req.redirect('/timeout')
        raise TimeoutError, "Volunteer's session timed out"
    
    
    return(user,volunteer)
  
  login = staticmethod(login)