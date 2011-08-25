import os,sys

from google.appengine.api import apiproxy_stub_map,memcache
from google.appengine.datastore import datastore_index
import operator
import wsgiref.handlers
import cgi, logging, traceback
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from controllers.events import EventsPage, EventAddCoordinatorPage

from controllers.paginated_event_pages import \
    PaginatedVolunteerCompletedPage, PaginatedNeighborhoodCompletedPage, \
    PaginatedCategoryCompletedPage, PaginatedVolunteerUpcomingPage, \
    PaginatedNeighborhoodUpcomingPage, PaginatedCategoryUpcomingPage, \
    PaginatedUpcomingPage, PaginatedRecommendedPage, PaginatedVolunteerHostedPage, \
    PaginatedVolunteerCoordinatedCompletedPage, PaginatedOngoingPage, \
    PaginatedNeighborhoodOngoingPage

from controllers.home import MainPage
from controllers.profile import ProfilePage

from controllers.accounts import Login, CreateAccount, HelpLogin, CreateOrganization

from controllers.eventvolunteers import VolunteerForEvent
from controllers.eventattendance import VerifyEventAttendance
from controllers.messages import Mailbox, Forum
from controllers.message_writer import SendMessage_Personal, SendMessage_Event, SendMessage_Neighborhood
from controllers.volunteers import VolunteersPage, FollowVolunteer, VolunteerAvatar
from controllers.organizations import OrganizationPage
from controllers.neighborhoods import NeighborhoodsPage, NeighborhoodDetailPage
from controllers.friends import FriendsPage 
from controllers.applications import AllApplications, ThisApplication
from controllers.mobile import CheckinPage

from controllers.paginated_volunteer_pages import \
    PaginatedTeamPage, PaginatedVolunteerCategoryPage, \
    PaginatedNeighborhoodVolunteerWorkPage, PaginatedNeighborhoodVolunteerHomePage, \
    PaginatedVolunteerTeam, PaginatedEventAttendeesPage

from controllers.static import StaticPage, CauseCrowdPage
from controllers.settings import SettingsPage
from controllers.interest_categories import CategoryPage

from controllers.abstract_handler import AbstractHandler
from google.appengine.ext.webapp.util import run_wsgi_app

webapp.template.register_template_library('controllers._filters')



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

def db_log(model, call, details=''):
    """Call this method whenever the database is invoked.

    Args:
        model: the model name (aka kind) that the operation is on
        call: the kind of operation (Get/Put/...)
        details: any text that should be added to the detailed log entry.
    """

    # First, let's update memcache
    if model:
        stats = memcache.get('DB_TMP_STATS')
        if stats is None: stats = {}
        key = '%s_%s' % (call, model)
        stats[key] = stats.get(key, 0) + 1
        memcache.set('DB_TMP_STATS', stats)

    # Next, let's log for some more detailed analysis
    logging.debug('DB_LOG: %s @ %s (%s)', call, model, details)
    
def patch_appengine():
    """Apply a hook to app engine that logs db statistics."""
    def model_name_from_key(key):
        return key.path().element_list()[0].type()
    
    def hook(service, call, request, response):
        logging.info('%s %s - %s' % (service, call, str(request)))
        stack = traceback.format_stack()
        logging.debug('%s %s - %s' % (service, call, "n".join(stack)))
    
    apiproxy_stub_map.apiproxy.GetPreCallHooks().Append(
           'db_log', hook, 'datastore_v3')
       
#patch_appengine()  
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
    debug = 'SERVER_SOFTWARE' not in os.environ or os.environ['SERVER_SOFTWARE'].startswith('Development')
    
    if debug:
        from utils.applications.operations import synchronize_apps
        from models.application import Application
        if Application.all().count() == 0:
            class hack(AbstractHandler):
                def sync(self):
                    logging.info('syncing')
                    synchronize_apps(server = self.get_server())
            hack().sync()
    
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication(
          [('/', MainPage),
           ('/incentives', MainPage),
           ('/rpx_auth', Login),
           ('/login', Login),
           ('/login/help', HelpLogin),
           ('/dev_login', Login),
           ('/logout', Login),           
           ('/new', CreateAccount),
           ('/neworg', CreateOrganization),
           
           ('/delete', SettingsPage),
           ('/profile', ProfilePage),
           ('/mobile/checkin(|/\d+)', CheckinPage),
           ('/messages(|/\d+)', Mailbox),
           ('/messages/(inbox|sent)', Mailbox),
           
           ('/settings', SettingsPage), #handles posts as well
           ('/settings/avatar', VolunteerAvatar),
           
           ('/events/(\d+)/volunteer', VolunteerForEvent),
           ('/events/(\d+)/add_coordinator', EventAddCoordinatorPage),
           ('/events/(\d+)/verify', VerifyEventAttendance),
           ('/events(|/\d+|/new|/search|/\d+/edit)', EventsPage),
           ('/events/(\d+)/attendees', PaginatedEventAttendeesPage),
           ('/events/past/volunteer/(\d+)', PaginatedVolunteerCompletedPage),  
           ('/events/past/coordinated/(\d+)', PaginatedVolunteerCoordinatedCompletedPage),    
  
           ('/events/past/neighborhood/(\d+)', PaginatedNeighborhoodCompletedPage),
           ('/events/past/category/(\d+)', PaginatedCategoryCompletedPage),
           ('/events/hosted/volunteer/(\d+)', PaginatedVolunteerHostedPage),
           ('/events/upcoming/volunteer/(\d+)', PaginatedVolunteerUpcomingPage),
           ('/events/upcoming/neighborhood/(\d+)', PaginatedNeighborhoodUpcomingPage),
           ('/events/ongoing/neighborhood/(\d+)', PaginatedNeighborhoodOngoingPage),
           ('/events/upcoming/category/(\d+)', PaginatedCategoryUpcomingPage),         
           ('/events/upcoming', PaginatedUpcomingPage),
           ('/events/ongoing', PaginatedOngoingPage),
           ('/events/recommended', PaginatedRecommendedPage),
           ('/events/(\d+)/send_message', SendMessage_Event),
           ('/events/(\d+)/messages', Forum),
           
           ('/neighborhoods/(\d+)', NeighborhoodDetailPage),
           ('/neighborhoods/(\d+)/volunteers_work', PaginatedNeighborhoodVolunteerWorkPage),
           ('/neighborhoods/(\d+)/volunteers_live', PaginatedNeighborhoodVolunteerHomePage),
           ('/neighborhoods(|)', NeighborhoodsPage),     
           ('/neighborhoods/(\d+)/send_message', SendMessage_Neighborhood),
           ('/neighborhoods/(\d+)/messages', Forum),
           
           ('/team', FriendsPage),
           ('/team/list', PaginatedTeamPage),
           
           ('/volunteers/(\d+)/follow', FollowVolunteer),
           ('/volunteers/(\d+)/avatar', VolunteerAvatar),
           ('/volunteers(|/\d+|/search)', VolunteersPage),
           ('/volunteers/(\d+)/team', PaginatedVolunteerTeam),
           ('/volunteers/(\d+)/send_message', SendMessage_Personal),
           
           ('/organizations(|/\d+|/search)', OrganizationPage),
           
           ('/category/(\d+)', CategoryPage),
           ('/category/(\d+)/volunteers', PaginatedVolunteerCategoryPage),
           ('/category(|)', CategoryPage),
           
           ('/static/(\w+)', StaticPage),
           ('/causecrowd(|/\w+)', CauseCrowdPage),
           ('/timeout', TimeoutPage),
           
           ('/api/applications/all', AllApplications), 
           ('/api/applications/this', ThisApplication),

          ],
          debug=debug)
    run_wsgi_app(application)

if __name__ == "__main__":
    #profile_main()
    
    real_main()
  
  


