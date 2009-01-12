import os

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from models import Volunteer

################################################################################
# Settings page
################################################################################
class DeleteVolunteerPage(webapp.RequestHandler):
  
  def get(self):
    user = users.get_current_user()

    if not user:
        self.redirect(users.create_login_url(self.request.uri))
        return

    volunteer = Volunteer.gql("where user = :user", user=user).get();
    if volunteer:
      volunteer.delete()
    
    self.response.out.write('volunteer removed')

################################################################################
# Settings page
################################################################################
class SettingsPage(webapp.RequestHandler):
  
  def get(self):
    user = users.get_current_user()

    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return

    volunteer = Volunteer.gql("where user = :user", user=user).get();
    
    if not volunteer:
      message = "Welcome newly registered volunteer"
      volunteer = Volunteer()
      volunteer.user = user
      volunteer.put();
    else:
      message = "Welcome back old volunteer"
      if volunteer.neighborhood:
        message += " from " + volunteer.neighborhood
      
    logout_url = users.create_logout_url(self.request.uri)
    template_values = {
        'logout_url': logout_url,
        'message': message,
      }
    path = os.path.join(os.path.dirname(__file__), 'settings.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):
    user = users.get_current_user()

    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return

    volunteer = Volunteer.gql("where user = :user", user=user).get();
    if volunteer and self.request.get('neighborhood'):
      #TODO:
      # Set neighborhoods up in DB
      # Verify that neighborhood input is in the DB
      volunteer.neighborhood = self.request.get('neighborhood')
      volunteer.put();
      
    if not volunteer:
      message = "Welcome new volunteer from " + self.request.get('neighborhood')
    else:
      message = "Welcome back old volunteer"
      if volunteer.neighborhood:
        message += " from " + volunteer.neighborhood
      

    logout_url = users.create_logout_url(self.request.uri)
    template_values = {
        'logout_url': logout_url,
        'message': message,
      }
    path = os.path.join(os.path.dirname(__file__), 'settings.html')
    self.response.out.write(template.render(path, template_values))

