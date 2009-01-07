import cgi
import wsgiref.handlers
import os
import logging


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

################################################################################
# models
################################################################################
class Volunteer(db.Model):
  user = db.UserProperty()
  neighborhood = db.StringProperty()

class Event(db.Model):
  name = db.StringProperty()
  date = db.DateProperty()
  neighborhood = db.StringProperty()
  
class EventVolunteer(db.Model):
  event = db.ReferenceProperty(Event,
                               required = True,
                               collection_name = 'volunteers')
  volunteer = db.ReferenceProperty(Volunteer,
                                    required = True,
                                    collection_name = 'events')
  isowner = db.BooleanProperty(required = True)

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


