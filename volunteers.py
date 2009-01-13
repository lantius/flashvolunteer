import os, string

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp

#TODO Do we need all these imports? I copied them
from models import Volunteer, Event, EventVolunteer, Neighborhood


################################################################################
# Events page
################################################################################
class VolunteersPage(webapp.RequestHandler):

  def get(self, url_data):
    user = users.get_current_user()
    logout_url =''

    if user:
      logout_url = users.create_logout_url(self.request.uri)
        
      user_volunteer = Volunteer.gql("where user = :user", user=user).get();
      if user_volunteer and user_volunteer.key().id() == int(url_data):
        self.redirect("/settings");
        return
    
    page_volunteer = Volunteer.get_by_id(int(url_data))
    
    template_values = { 'eventvolunteer': page_volunteer.ev_set, 'volunteer': page_volunteer, 'logout_url': logout_url}
    path = os.path.join(os.path.dirname(__file__), 'volunteer.html')
    self.response.out.write(template.render(path, template_values))