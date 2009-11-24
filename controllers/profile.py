import os
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.api import memcache
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
            account = self.auth(require_login=True)
        except:
            return    
        
        user = account.get_user()
        
        events = { 'Your events' : user.events() }
        byinterest = []
        
        if user.home_neighborhood:
            events['Neighborhood events'] = user.home_neighborhood.events
        
        for ic in user.interestcategories():
            if ic.events():
                byinterest.append(ic)
        
        recommended_events = user.recommended_events()[:ProfilePage.LIMIT]
        my_future_events = user.events_future().fetch(ProfilePage.LIMIT)
        
        past_events = memcache.get('past_events')
        searchurl = memcache.get('searchurl')
        
        template_values = {
            'volunteer' : user,
            'neighborhoods': NeighborhoodHelper().selected(user.home_neighborhood),
            'recommended_events': recommended_events,
            'my_future_events': my_future_events,
            #TODO: convert to application-specific data model
            'interest_categories': InterestCategory.all(),
            'past_events': past_events,
            'searchurl': searchurl
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', 'views', 'volunteers', 'profile.html')
        self.response.out.write(template.render(path, template_values))