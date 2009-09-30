import os
import wsgiref.handlers
import cgi, logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from controllers.events import EventsPage, EventAddCoordinatorPage

from controllers.paginated_event_pages import \
    PaginatedVolunteerCompletedPage, PaginatedNeighborhoodCompletedPage, \
    PaginatedCategoryCompletedPage, PaginatedVolunteerUpcomingPage, \
    PaginatedNeighborhoodUpcomingPage, PaginatedCategoryUpcomingPage, \
    PaginatedUpcomingPage, PaginatedRecommendedPage, PaginatedVolunteerHostedPage         

from controllers.home import MainPage
from controllers.profile import ProfilePage

from controllers.accounts import AccountPage, RPXTokenHandler

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
         ('/rpx_response', RPXTokenHandler),
         ('/create', AccountPage),
         ('/login', AccountPage),
         ('/dev_login', AccountPage),
         ('/logout', AccountPage),
          ('/delete', SettingsPage),
         ('/profile', ProfilePage),
         ('/settings', SettingsPage), #handles posts as well
         ('/settings/avatar', VolunteerAvatar),
         ('/events/(\d+)/volunteer', VolunteerForEvent),
         ('/events/(\d+)/add_coordinator', EventAddCoordinatorPage),
         ('/events/(\d+)/messages(|/\d+|/new)', EventMessagesPage),
         ('/events/(\d+)/verify', VerifyEventAttendance),
         ('/events(|/\d+|/new|/search|/\d+/edit)', EventsPage),
         ('/events/(\d+)/attendees/(\d+)', PaginatedEventAttendeesPage),

         ('/events/past/volunteer/(\d+)/(\d+)', PaginatedVolunteerCompletedPage),    
         ('/events/past/neighborhood/(\d+)/(\d+)', PaginatedNeighborhoodCompletedPage),
         ('/events/past/category/(\d+)/(\d+)', PaginatedCategoryCompletedPage),
              
         ('/events/hosted/volunteer/(\d+)/(\d+)', PaginatedVolunteerHostedPage),
         ('/events/upcoming/volunteer/(\d+)/(\d+)', PaginatedVolunteerUpcomingPage),
         ('/events/upcoming/neighborhood/(\d+)/(\d+)', PaginatedNeighborhoodUpcomingPage),
         ('/events/upcoming/category/(\d+)/(\d+)', PaginatedCategoryUpcomingPage),         
         ('/events/upcoming/(\d+)', PaginatedUpcomingPage),
         ('/events/recommended/(\d+)', PaginatedRecommendedPage),
         
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
         ('/category(|)', CategoryPage),
         ('/static/(\w+)', StaticPage),
         ('/timeout', TimeoutPage),
        ],
        debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
  
  


