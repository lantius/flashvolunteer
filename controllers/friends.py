from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template
import os

################################################################################
# Friends page
################################################################################
class FriendsPage(webapp.RequestHandler):
  def get(self):    
    
    user = users.get_current_user()
    if user:
      logout_url = users.create_logout_url(self.request.uri)
    else:
      logout_url = ""

    template_values = {
        'logout_url': logout_url,
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'friends.html')
    self.response.out.write(template.render(path, template_values))
    return
