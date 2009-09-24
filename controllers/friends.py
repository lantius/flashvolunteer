from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os
import random 

from controllers._auth import Authorize
from controllers._helpers import NeighborhoodHelper

################################################################################
# Friends page
################################################################################
class FriendsPage(webapp.RequestHandler):
  def get(self): 
    LIMIT = 12
    
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return
    candidates = list(volunteer.friends()) + list(volunteer.following_only())
    
    friends = random.sample(candidates,min(len(candidates),LIMIT))
    template_values = {
        'volunteer': volunteer,
        'neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
        'friends': friends,
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'team.html')
    self.response.out.write(template.render(path, template_values))
    return