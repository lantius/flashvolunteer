import os
import wsgiref.handlers
import cgi, logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from controllers.events import EventsPage, \
    EventVolunteerCompletedPage, EventNeighborhoodCompletedPage, EventCategoryCompletedPage, \
    EventVolunteerUpcomingPage, EventNeighborhoodUpcomingPage, EventCategoryUpcomingPage, \
    EventUpcomingPage, EventRecommendedPage         

from controllers.home import MainPage
from controllers.eventvolunteers import VolunteerForEvent
from controllers.eventattendance import VerifyEventAttendance
from controllers.eventmessages import EventMessagesPage
from controllers.volunteers import VolunteersPage, FollowVolunteer, VolunteerAvatar
from controllers._helpers import InitializeStore
from controllers.neighborhoods import NeighborhoodsPage, NeighborhoodDetailPage
from controllers.friends import FriendsPage 

from controllers.paginated_volunteer_pages import \
    PaginatedTeamPage, PaginatedVolunteerCategoryPage, \
    PaginatedNeighborhoodVolunteerWorkPage, PaginatedNeighborhoodVolunteerHomePage, \
    PaginatedVolunteerTeam, PaginatedEventAttendeesPage

from controllers.static import StaticPage
from controllers.settings import SettingsPage
from controllers.interest_categories import CategoryPage
from controllers.admin import AdminPage


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
         ('/admin', AdminPage),
         ('/settings', SettingsPage), #handles posts as well
         ('/settings/avatar', VolunteerAvatar),
         ('/delete', SettingsPage),
         ('/events/(\d+)/volunteer', VolunteerForEvent),
         ('/events/(\d+)/messages(|/\d+|/new)', EventMessagesPage),
         ('/events/(\d+)/verify', VerifyEventAttendance),
         ('/events(|/\d+|/new|/search|/\d+/edit)', EventsPage),
         ('/events/(\d+)/attendees/(\d+)', PaginatedEventAttendeesPage),

         ('/events/past/volunteer/(\d+)/(\d+)', EventVolunteerCompletedPage),    
         ('/events/past/neighborhood/(\d+)/(\d+)', EventNeighborhoodCompletedPage),
         ('/events/past/category/(\d+)/(\d+)', EventCategoryCompletedPage),                  
              
         ('/events/upcoming/volunteer/(\d+)/(\d+)', EventVolunteerUpcomingPage),
         ('/events/upcoming/neighborhood/(\d+)/(\d+)', EventNeighborhoodUpcomingPage),
         ('/events/upcoming/category/(\d+)/(\d+)', EventCategoryUpcomingPage),         
         ('/events/upcoming/(\d+)', EventUpcomingPage),
         ('/events/recommended/(\d+)', EventRecommendedPage),
         
         ('/neighborhoods/(\d+)', NeighborhoodDetailPage),
         ('/neighborhoods/(\d+)/volunteers_work/(\d+)', PaginatedNeighborhoodVolunteerWorkPage),
         ('/neighborhoods/(\d+)/volunteers_live/(\d+)', PaginatedNeighborhoodVolunteerHomePage),
         ('/neighborhoods(|)', NeighborhoodsPage),     
         ('/team', FriendsPage),
         ('/team/(\d+)', PaginatedTeamPage),
         ('/volunteers/(\d+)/follow', FollowVolunteer),
         ('/volunteers/(\d+)/avatar', VolunteerAvatar),
         ('/volunteers(|/\d+|/search)', VolunteersPage),
         ('/volunteers/(\d+)/team/(\d+)', PaginatedVolunteerTeam),
         ('/category/(\d+)', CategoryPage),
         ('/category/(\d+)/volunteers/(\d+)', PaginatedVolunteerCategoryPage),
         ('/static/(\w+)', StaticPage),
         ('/timeout', TimeoutPage),
        ],
        debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
  
  


