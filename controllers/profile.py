import os
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from controllers._auth import Authorize
from controllers._helpers import NeighborhoodHelper

from models.volunteer import Volunteer
from models.neighborhood import Neighborhood
from models.event import Event
from models.interestcategory import InterestCategory

from controllers.events import _get_recommended_events, _get_upcoming_events 

from controllers.abstract_handler import AbstractHandler

################################################################################
# ProfilePage
class ProfilePage(AbstractHandler):
  LIMIT = 3 
  def get(self):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/login')
    except:
      return    

    events = { 'Your events' : volunteer.events() }
    byinterest = []
    
    if volunteer.home_neighborhood:
      events['Neighborhood events'] = volunteer.home_neighborhood.events
    
    for ic in volunteer.interestcategories():
      if ic.events():
        byinterest.append(ic)

    recommended_events = list(_get_recommended_events(volunteer = volunteer))[:ProfilePage.LIMIT]
    my_future_events = volunteer.events_future()[:ProfilePage.LIMIT]

    template_values = {
        'volunteer' : volunteer,
        'neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
        'recommended_events': recommended_events,
        'my_future_events': my_future_events,
        #TODO: convert to application-specific data model
        'interest_categories': InterestCategory.all()
      }
    self._add_base_template_values(vals = template_values)
    
    path = os.path.join(os.path.dirname(__file__), '..', 'views', 'volunteers', 'profile.html')
    self.response.out.write(template.render(path, template_values))