import os
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from controllers._auth import Authorize
from controllers._helpers import NeighborhoodHelper

from models.neighborhood import Neighborhood
from models.interestcategory import InterestCategory

from controllers.abstract_handler import AbstractHandler

################################################################################
# ProfilePage
class ProfilePage(AbstractHandler):
    LIMIT = 2
    def get(self):
        try:
            volunteer = Authorize.login(self, requireVolunteer=True)
        except:
            return    
        
        events = { 'Your events' : volunteer.events() }
        byinterest = []
        
        if volunteer.home_neighborhood:
            events['Neighborhood events'] = volunteer.home_neighborhood.events
        
        for ic in volunteer.interestcategories():
            if ic.events():
                byinterest.append(ic)
        
        recommended_events = list(volunteer.recommended_events())[:ProfilePage.LIMIT]
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