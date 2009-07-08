import os
import wsgiref.handlers
import cgi, logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from controllers.home import MainPage
from controllers.events import EventsPage
from controllers.eventvolunteers import VolunteerForEvent
from controllers.eventattendance import VerifyEventAttendance, EventAttendeesPage
from controllers.eventmessages import EventMessagesPage
from controllers.volunteers import VolunteersPage, FollowVolunteer, VolunteerAvatar, VolunteerTeam
from controllers._helpers import InitializeStore
from controllers.neighborhoods import NeighborhoodsPage, NeighborhoodDetailPage
from controllers.friends import FriendsPage, AllFriendsPage
from controllers.static import StaticPage
from controllers.settings import SettingsPage
from controllers.interest_categories import CategoryPage

webapp.template.register_template_library('templatetags.filters')

################################################################################
# Timeout page
class TimeoutPage(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), '..', 'views','session_timeout.html')
    self.response.out.write(template.render(path, {}))

################################################################################
# gae mojo

# /events GET: display the list of events you own, or are signed up for. 
# /events POST: create a new event

# /events/1 GET: display the detail page for an event
# /events/1 POST: update an event

# /events/1/volunteer GET: ??
# /events/1/volunteer POST: sign up for an event
# /events/1/volunteer?delete=true POST: unsign up for an event
# /events/1?delete=true POST: delete up for an event

def main():
  init = InitializeStore()
  init.init()
  logging.getLogger().setLevel(logging.DEBUG)
  application = webapp.WSGIApplication(
        [('/', MainPage),
         ('/settings', SettingsPage), #handles posts as well
         ('/settings/avatar', VolunteerAvatar),
         ('/delete', SettingsPage),
         ('/events/(\d+)/volunteer', VolunteerForEvent),
         ('/events/(\d+)/messages(|/\d+|/new)', EventMessagesPage),
         ('/events/(\d+)/verify', VerifyEventAttendance),
         ('/events(|/\d+|/new|/search|/\d+/edit)', EventsPage),
         ('/events/(\d+)/attendees/(\d+)', EventAttendeesPage),
         ('/neighborhoods/(\d+)', NeighborhoodDetailPage),
         ('/neighborhoods(|)', NeighborhoodsPage),     
         ('/team', FriendsPage),
         ('/team/(\d+)', AllFriendsPage),
         ('/volunteers/(\d+)/follow', FollowVolunteer),
         ('/volunteers/(\d+)/avatar', VolunteerAvatar),
         ('/volunteers(|/\d+|/search)', VolunteersPage),
         ('/volunteers/(\d+)/team/(\d+)', VolunteerTeam),
         ('/category/(\d+)', CategoryPage),
         ('/static/(\w+)', StaticPage),
         ('/timeout', TimeoutPage),
        ],
        debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
  
  


