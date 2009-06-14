import os
import wsgiref.handlers
import cgi, logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from controllers.home import MainPage
from controllers.events import EventsPage, VolunteerForEvent, EditEventPage, VerifyEventAttendance
from controllers.eventmessages import EventMessagesPage
from controllers.volunteers import VolunteersPage, FollowVolunteer, VolunteerAvatar
from controllers._helpers import InitializeStore
from controllers.neighborhoods import NeighborhoodsPage, NeighborhoodDetailPage
from controllers.friends import FriendsPage
from controllers.help import HelpPage
from controllers.settings import SettingsPage

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
                                     ('/delete', SettingsPage),
                                     ('/events/(\d+)/volunteer', VolunteerForEvent),
                                     ('/events/(\d+)/edit', EditEventPage),
                                     ('/events/(\d+)/messages(|/\d+|/new)', EventMessagesPage),
                                     ('/events/(\d+)/verify', VerifyEventAttendance),
                                     ('/events(|/\d+|/new|/search)', EventsPage),
                                     ('/neighborhoods/(\d+)', NeighborhoodDetailPage),
                                     ('/neighborhoods(|)', NeighborhoodsPage),     
                                     ('/team', FriendsPage),
                                     ('/volunteers/(\d+)/follow', FollowVolunteer),
                                     ('/volunteers/(\d+)/avatar', VolunteerAvatar),
                                     ('/volunteers(|/\d+)', VolunteersPage),
                                     ('/help', HelpPage),
                                     ('/timeout', TimeoutPage),
                                    ],
                                    debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
  
  


