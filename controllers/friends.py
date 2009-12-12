from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os
import random 
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
            account = self.auth(require_login=True)
        except:
            return       
    
        volunteer = account.get_user()
        candidates = list(volunteer.following(limit = 250))
                     
#        volunteer_stats = memcache.get('volunteer_stats')
#        if not volunteer_stats: 
#            volunteers = get_all_volunteers()
#            all_scores = []
#                                      
#            for v in volunteers:
#                vhours = sum([ev.hours for ev in v.eventvolunteers if ev.hours])
#                attended = len([ev for ev in v.eventvolunteers if ev.attended])
#                isowner = len([ev for ev in v.eventvolunteers if ev.isowner]) 
#
#                total = attended + isowner
#                all_scores.append((v, total, [attended, isowner]))
#    
#            all_scores.sort(lambda (ev, total, scores), (ev2, total2, scores2): int(total-total2), reverse=True)                                                                    
#            
#            volunteer_stats = []
#            for v, total, scores in all_scores:
#                #scores.append(total)  #dont show total score at this time...
#                volunteer_stats.append((v, scores))
#            memcache.add('volunteer_stats', volunteer_stats, 10000)
        
        friends = random.sample(candidates,min(len(candidates),LIMIT))
        template_values = {
            'volunteer': volunteer,
            'neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
            'friends': friends,
            'followers_only': (v for v in volunteer.followers_only()),
            #'most_active_volunteers': volunteer_stats[:LIMIT2],
          }
        self._add_base_template_values(vals = template_values)                   
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'team.html')
        self.response.out.write(template.render(path, template_values))
        return

def get_all_volunteers():
    vols = []
    CHUNK_SIZE = 10
    
    last_key = None
    while True:
        if last_key:
            query = Volunteer.gql('WHERE __key__ > :1 ORDER BY __key__', last_key)
        else:
            query = Volunteer.gql('ORDER BY __key__')
        
        vol_in_chunk = query.fetch(limit = CHUNK_SIZE + 1)
        
        if len(vol_in_chunk) == CHUNK_SIZE + 1:
            vols += vol_in_chunk[:-1]
            last_key = vol_in_chunk[-1].key()
        else:
            vols += vol_in_chunk
            break
    return vols
