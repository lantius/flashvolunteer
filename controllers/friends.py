from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os
import random 
from models.eventvolunteer import EventVolunteer
from controllers._auth import Authorize
from controllers._helpers import NeighborhoodHelper
from models.event import Event
from controllers.abstract_handler import AbstractHandler
from controllers._utils import get_application
from models.volunteer import Volunteer
from google.appengine.api import memcache

################################################################################
# Friends page
################################################################################
class FriendsPage(AbstractHandler):
    def get(self): 
        LIMIT = 12
        LIMIT2 = 15
        try:
            volunteer = Authorize.login(self, requireVolunteer=True)
        except:
            return       
    
        candidates = list(volunteer.friends()) + list(volunteer.following_only())
        volunteers = Volunteer.all().fetch(limit=500)
             
        volunteer_stats = memcache.get('volunteer_stats')
        if not volunteer_stats: 
            stats = {}       
                                      
            for v in volunteers:
                vhours = 0
                attended = 0
                isowner = 0
                                                  
                for ev in v.account.eventvolunteers:                
                    vhours += sum([ev.hours for ev in v.eventvolunteers if ev.hours])
                    attended += sum([ev.attended for ev in v.eventvolunteers if ev.attended])
                    isowner += sum([ev.isowner for ev in v.eventvolunteers if ev.isowner]) 

                        
                stats[v] = [attended,isowner]          
            
            all_scores = []                                             
            for ev,scores in stats.items():
                if sum(scores):
                    all_scores.append((ev, sum(scores), scores))
    
            all_scores.sort(lambda (ev, total, scores), (ev2, total2, scores2): int(total-total2), reverse=True)                                                                    
            
            volunteer_stats = []
            for v, total, scores in all_scores:
                #scores.append(total)  #dont show total score at this time...
                volunteer_stats.append((v, scores))
            memcache.add('volunteer_stats', volunteer_stats, 10000)
        
        friends = random.sample(candidates,min(len(candidates),LIMIT))
        template_values = {
            'volunteer': volunteer,
            'neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
            'friends': friends,
            'most_active_volunteers': volunteer_stats[:LIMIT2],
          }
        self._add_base_template_values(vals = template_values)                   
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'team.html')
        self.response.out.write(template.render(path, template_values))
        return