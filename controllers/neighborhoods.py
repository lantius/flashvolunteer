from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template
import os

from controllers._auth import Authorize

################################################################################
# Neighborhoods page
################################################################################
class NeighborhoodsPage(webapp.RequestHandler):
  def get(self, url_data):    
    try:
      volunteer = Authorize.login(self, requireVolunteer=False, redirectTo='settings')
    except:
      return
    
    template_values = {
        'volunteer': volunteer,
      }

    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhoods.html')
    self.response.out.write(template.render(path, template_values))
    return
    