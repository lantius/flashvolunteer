import os, string

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp

from controllers._auth import Authorize

from models import Volunteer


################################################################################
# Events page
################################################################################
class VolunteersPage(webapp.RequestHandler):

  def get(self, url_data):
    (user, volunteer) = Authorize.login(self)

    logout_url =''

    if user:
      logout_url = users.create_logout_url(self.request.uri)
        
      user_volunteer = Volunteer.gql("where user = :user", user=user).get();
      if user_volunteer and user_volunteer.key().id() == int(url_data):
        self.redirect("/settings");
        return
    
    page_volunteer = Volunteer.get_by_id(int(url_data))
    
    template_values = { 'eventvolunteer': page_volunteer.eventvolunteers, 'volunteer': page_volunteer, 'logout_url': logout_url}
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteer.html')
    self.response.out.write(template.render(path, template_values))