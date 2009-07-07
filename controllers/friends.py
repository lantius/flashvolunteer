from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

from controllers._auth import Authorize
from controllers._helpers import NeighborhoodHelper


################################################################################
# Friends page
################################################################################
class FriendsPage(webapp.RequestHandler):
  def get(self):    
    try:
      volunteer = Authorize.login(self, requireVolunteer=False, redirectTo='/settings')
    except:
      return
    
    template_values = {
        'volunteer': volunteer,
        'session_id' : volunteer.session_id,
        'neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'team.html')
    self.response.out.write(template.render(path, template_values))
    return
