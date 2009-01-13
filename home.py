import cgi
import wsgiref.handlers
import os
import logging

from settings import SettingsPage, DeleteVolunteerPage
from models import Volunteer, Neighborhood
from events import EventsPage, VolunteerForEvent
from volunteers import VolunteersPage

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
      settings_text = "Create an account"
      events_text= ""
      events=""
    else:
      message = "Welcome back old volunteer " + volunteer.user.nickname()
      settings_text = "Account Settings"
      events_text="create_an event!"
      if volunteer.neighborhood:
        message += " from " + volunteer.neighborhood.name
        events = volunteer.neighborhood.events
        
    logout_url = users.create_logout_url(self.request.uri)
    template_values = {
        'logout_url': logout_url,
        'message': message,
        'events_text': events_text,
        'settings_text': settings_text,
        'events' : events,
      }
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class InitializeStore(webapp.RequestHandler):
  def get(self):
    neighborhoods = ("Capital Hill", "West Seattle", "University District", "Wedgewood")
    for neighborhood_name in neighborhoods:
      n = Neighborhood(name=neighborhood_name)
      n.put()
    
    
################################################################################
# gae mojo
################################################################################

# /events GET: display the list of events you own, or are signed up for. 
# /events POST: create a new event

# /events/1 GET: display the detail page for an event
# /events/1 POST: update an event

# /events/1/volunteer GET: ??
# /events/1/volunteer POST: sign up for an event
# /events/1/volunteer?delete=true POST: unsign up for an event
# /events/1?delete=true POST: delete up for an event

def main():
  logging.getLogger().setLevel(logging.DEBUG)
  application = webapp.WSGIApplication(
                                    [('/', MainPage),
                                     ('/settings', SettingsPage), #handles posts as well
                                     ('/delete', DeleteVolunteerPage),
                                     ('/events/(\d+)/volunteer', VolunteerForEvent),
                                     #TODO break out cases to be explicit below
                                     ('/events(|/.*)', EventsPage), #handles posts as well
                                     ('/_init', InitializeStore),
                                     ('/volunteers/(\d+)', VolunteersPage)
                                    ],
                                    debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()


