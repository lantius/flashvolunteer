import os
import wsgiref.handlers
import cgi, logging
from components.sessions import Session

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

from controllers.accounts import Login, CreateAccount

from controllers.eventvolunteers import VolunteerForEvent
from controllers.eventattendance import VerifyEventAttendance
from controllers.messages import Mailbox
from controllers.message_writer import SendMessage_Personal
from controllers.volunteers import VolunteersPage, FollowVolunteer, VolunteerAvatar
from controllers.neighborhoods import NeighborhoodsPage, NeighborhoodDetailPage
from controllers.friends import FriendsPage 
from controllers.applications import AllApplications, ThisApplication

from controllers.paginated_volunteer_pages import \
    PaginatedTeamPage, PaginatedVolunteerCategoryPage, \
    PaginatedNeighborhoodVolunteerWorkPage, PaginatedNeighborhoodVolunteerHomePage, \
    PaginatedVolunteerTeam, PaginatedEventAttendeesPage

from controllers.static import StaticPage
from controllers.settings import SettingsPage
from controllers.interest_categories import CategoryPage

from controllers.abstract_handler import AbstractHandler

from controllers._utils import get_server, is_debugging

webapp.template.register_template_library('templatetags.filters')

################################################################################
# Timeout page
class TimeoutPage(AbstractHandler):
    def get(self):
        template_values = {}
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', 'views','session_timeout.html')
        self.response.out.write(template.render(path, template_values))

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


def profile_main():
    # This is the main function for profiling 
    # We've renamed our original main() above to real_main()
    import cProfile, pstats, StringIO
    prof = cProfile.Profile()
    prof = prof.runctx("real_main()", globals(), locals())
    stream = StringIO.StringIO()
    stats = pstats.Stats(prof, stream=stream)
    stats.sort_stats("time")  # Or cumulative
    stats.print_stats(80)  # 80 = how many to print
    # The rest is optional.
    # stats.print_callees()
    # stats.print_callers()
    logging.info("Profile data:\n%s", stream.getvalue())
 
 
def real_main():
    debug = is_debugging()
    if debug:
        from components.applications.operations import synchronize_apps
        from models.application import Application
        if Application.all().count() == 0:
            synchronize_apps()
        
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication(
          [('/', MainPage),
           ('/rpx_auth', Login),
           ('/create', Login),
           ('/login', Login),
           ('/dev_login', Login),
           ('/logout', Login),
           
           ('/new', CreateAccount),
           
            ('/delete', SettingsPage),
           ('/profile', ProfilePage),
           ('/messages(|/\d+)', Mailbox),
           
           ('/settings', SettingsPage), #handles posts as well
           ('/settings/avatar', VolunteerAvatar),
           
           ('/events/(\d+)/volunteer', VolunteerForEvent),
           ('/events/(\d+)/add_coordinator', EventAddCoordinatorPage),
    #         ('/events/(\d+)/contact_volunteers', Event)
           #('/events/(\d+)/messages(|/\d+|/new)', EventMessagesPage),
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
           ('/volunteers/(\d+)/send_message', SendMessage_Personal),
           
           ('/category/(\d+)', CategoryPage),
           ('/category/(\d+)/volunteers/(\d+)', PaginatedVolunteerCategoryPage),
           ('/category(|)', CategoryPage),
           
           ('/static/(\w+)', StaticPage),
           ('/timeout', TimeoutPage),
           
           ('/api/applications/all', AllApplications), 
           ('/api/applications/this', ThisApplication)
          ],
          debug=debug)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    #profile_main
    real_main()
  
  


