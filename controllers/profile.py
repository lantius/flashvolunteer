import os, random, logging

from google.appengine.ext.webapp import template
from controllers._helpers import NeighborhoodHelper

from models.interestcategory import InterestCategory

from controllers.abstract_handler import AbstractHandler

################################################################################
# ProfilePage
class ProfilePage(AbstractHandler):
    LIMIT = 2
    def get(self):
        try:
            volunteer = self.auth(require_login=True)
        except:
            return    
        
        events = { 'Your events' : volunteer.events() }
        
        if volunteer.home_neighborhood:
            events['Neighborhood events'] = volunteer.home_neighborhood.events
        
        recommended_events = volunteer.recommended_events(application = self.get_application(),
                                                     session = self._session())[:ProfilePage.LIMIT]

        (future_events, past_events, 
         events_coordinating, past_events_coordinated) = volunteer.get_activities(ProfilePage.LIMIT)
        
        (future_events_cnt, past_events_cnt, 
         events_coordinating_cnt, past_events_coordinated_cnt) = volunteer.get_activities()
        
        vhours = sum([ev.hours for ev in volunteer.eventvolunteers if ev.hours])
        
        friends = volunteer.friends()
        if len(friends) > 5:
            friends = random.sample(friends, 5)
            
        template_values = {
            'volunteer' : volunteer,
            'neighborhoods': NeighborhoodHelper().selected(self.get_application(),volunteer.home_neighborhood),
            'recommended_events': recommended_events,
            #TODO: convert to application-specific data model
            'interest_categories': InterestCategory.all(),
            
            'past_events': past_events,
            'future_events': future_events,
            'past_events_coordinated': past_events_coordinated,
            'events_coordinating': events_coordinating,

            'past_events_cnt': past_events_cnt,
            'future_events_cnt': future_events_cnt,
            'past_events_coordinated_cnt': past_events_coordinated_cnt,
            'events_coordinating_cnt': events_coordinating_cnt,
            
            'user_of_interest': volunteer,
            'event_access': True,
            'friends': friends
            
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', 'views', 'volunteers', 'profile.html')
        self.response.out.write(template.render(path, template_values))