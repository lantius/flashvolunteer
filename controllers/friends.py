from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

from controllers._auth import Authorize

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
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'friends.html')
    self.response.out.write(template.render(path, template_values))
    return
