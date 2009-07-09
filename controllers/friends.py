from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os
import random 

from controllers._auth import Authorize
from controllers._helpers import NeighborhoodHelper


################################################################################
# Friends page
################################################################################
class FriendsPage(webapp.RequestHandler):
  def get(self): 
    LIMIT = 12
   
    try:
      volunteer = Authorize.login(self, requireVolunteer=False, redirectTo='/settings')
    except:
      return
    candidates = list(volunteer.friends())
    
    friends = random.sample(candidates,min(len(candidates),LIMIT))
    template_values = {
        'volunteer': volunteer,
        'session_id' : volunteer.session_id,
        'neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
        'friends': friends,
        'following_only': volunteer.following_only()
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'team.html')
    self.response.out.write(template.render(path, template_values))
    return


################################################################################
# AllFriendsPage

class AllFriendsPage(webapp.RequestHandler):

  def get(self, page):
    if page:
      self.show(int(page))

  def show(self, page):
    LIMIT = 12
    
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return
              
    total = volunteer.volunteerfollowing.count()
    start = (page-1) * LIMIT + 1
    offset = start - 1
    team = list(volunteer.friends()) + list(volunteer.following_only())
    team = [v for v in team[offset:offset+LIMIT]]

    end = start + len(team) - 1
                                                
    if end == total:
        next_page = -1
    else: 
        next_page = page + 1
    
    if page == 1:
        prev_page = -1
    else:
        prev_page = page -1
        
    template_values = { 
                        'volunteer' : volunteer,
                        'session_id' : volunteer.session_id,
                        'total': total,
                        'start': start,
                        'end': end,
                        'next_page': next_page,
                        'prev_page': prev_page,

                        'team': team,
                        'title': 'My FlashTeam',
                        'url': '/team/'
                        }
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'person_lists', '_paginated_volunteer_page.html')
    self.response.out.write(template.render(path, template_values))