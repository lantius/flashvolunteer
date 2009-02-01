import cgi
import wsgiref.handlers
import os
import logging

from controllers._auth import Authorize

from controllers.settings import SettingsPage, DeleteVolunteerPage
from models import Volunteer, Neighborhood, Event, InterestCategory
from controllers.events import EventsPage, VolunteerForEvent, EditEventPage
from controllers.volunteers import VolunteersPage

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

################################################################################
# MainPage
################################################################################
class MainPage(webapp.RequestHandler):
  
  def get(self):
    (user, volunteer) = Authorize.login(self)
    events=""
    
    if not volunteer:
      message = "Welcome volunteer"
      settings_text = "Create an account"
      events_text= ""
      events = { 'Upcoming events' : Event.all() }
    else:
      message = "Welcome back old volunteer " + volunteer.user.nickname()
      settings_text = "Account Settings"
      events_text="create_an event!"
      
      events = { 'Your events' : volunteer.events() }
      
      if volunteer.neighborhood:
        message += " from " + volunteer.neighborhood.name
        events['Neighborhood events'] = volunteer.neighborhood.events
        
    logout_url = users.create_logout_url(self.request.uri)
    template_values = {
        'logout_url': logout_url,
        'message': message,
        'events_text': events_text,
        'settings_text': settings_text,
        'events' : events,
      }
    path = os.path.join(os.path.dirname(__file__), '..', 'views', 'index.html')
    self.response.out.write(template.render(path, template_values))

class InitializeStore(webapp.RequestHandler):
  def get(self):
    neighborhoods = ("Capital Hill", "West Seattle", "University District", "Wedgewood")
    for neighborhood_name in neighborhoods:
      n = Neighborhood(name=neighborhood_name)
      n.put()
    
    categories = ("Animals","Arts & Culture","Children & Youth", "Education & Literacy", 
                  "Environment", "Gay, Lesbian, Bi, & Transgender", "Homeless & Housing",
                  "Hunger", "Justice & Legal", "Senior Citizens")
    for category_name in categories:
      c = InterestCategory(name = category_name)
      c.put()


class TimeoutPage(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), '..', 'views','session_timeout.html')
    self.response.out.write(template.render(path, ''))
    

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
                                     ('/events/(\d+)/edit', EditEventPage),
                                     ('/events(|/\d+)', EventsPage),                                
                                     #TODO break out cases to be explicit below
                                     ('/_init', InitializeStore),
                                     ('/volunteers/(\d+)', VolunteersPage),
                                     ('/timeout', TimeoutPage),
                                    ],
                                    debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()

