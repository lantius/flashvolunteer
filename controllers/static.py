from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

from controllers._auth import Authorize

################################################################################
# Help page
################################################################################
class StaticPage(webapp.RequestHandler):
  def get(self, urldata):    
    
    try:
      volunteer = Authorize.login(self, requireVolunteer=False, redirectTo='/settings')
    except:
      return
    
    template_values = {
        'volunteer': volunteer,
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'static', urldata + '.html')
    self.response.out.write(template.render(path, template_values))
    return