import os
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

        (future_events, past_events, 
         events_coordinating, past_events_coordinated) = user.get_activities(ProfilePage.LIMIT)
        
        (future_events_cnt, past_events_cnt, 
         events_coordinating_cnt, past_events_coordinated_cnt) = user.get_activities()
        
        vhours = sum([ev.hours for ev in user.eventvolunteers if ev.hours])
        
                
        template_values = {
            'volunteer' : user,
            'neighborhoods': NeighborhoodHelper().selected(user.home_neighborhood),
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
            
            'user_of_interest': user,
            'event_access': True
            
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', 'views', 'volunteers', 'profile.html')
        self.response.out.write(template.render(path, template_values))