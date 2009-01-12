import cgi
import wsgiref.handlers
import os
import logging

from models import Volunteer
from settings import SettingsPage
from settings import DeleteVolunteerPage

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

################################################################################
# MainPage
################################################################################
class MainPage(webapp.RequestHandler):
  
  def get(self):
    user = users.get_current_user()

    if not user:
        self.redirect(users.create_login_url(self.request.uri))
        return

    volunteer = Volunteer.gql("where user = :user", user=user).get();
    
    if not volunteer:
      message = "Welcome volunteer"
    else:
      message = "Welcome back old volunteer"
      if volunteer.neighborhood:
        message += " from " + volunteer.neighborhood
      
    logout_url = users.create_logout_url(self.request.uri)
    template_values = {
        'logout_url': logout_url,
        'message': message,
      }
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

################################################################################
# gae mojo
################################################################################
def main():
  logging.getLogger().setLevel(logging.DEBUG)
  application = webapp.WSGIApplication(
                                    [('/', MainPage),
                                     ('/settings', SettingsPage), #handles posts as well
                                     ('/delete', DeleteVolunteerPage),
                                    ],
                                    debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()


