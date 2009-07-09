from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os, random

from controllers._auth import Authorize
from models.neighborhood import Neighborhood

################################################################################
# Neighborhoods page
################################################################################
class NeighborhoodsPage(webapp.RequestHandler):
  def get(self, url_data):    
    try:
      volunteer = Authorize.login(self, requireVolunteer=False, redirectTo='/settings')
    except:
      return
    
    neighborhoods = sorted(Neighborhood.all(), lambda a,b:cmp(a.name,b.name))
    cnt = len(neighborhoods)
    col1 = neighborhoods[:cnt/3]
    col2 = neighborhoods[cnt/3:2*cnt/3]
    col3 = neighborhoods[2*cnt/3:]
    
    template_values = {
        'volunteer': volunteer,
        'neighborhoods1': col1,
        'neighborhoods2': col2,
        'neighborhoods3': col3 
      }

    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhoods.html')
    self.response.out.write(template.render(path, template_values))
    return
    
class NeighborhoodDetailPage(webapp.RequestHandler):
  ################################################################################
  # GET
  def get(self, url_data):
    if url_data:
      self.show(url_data)
    else:
      self.list() 

  ################################################################################
  # POST

  ################################################################################
  # SHOW
  def show(self, neighborhood_id):
    LIMIT = 12
    try:
      volunteer = Authorize.login(self, requireVolunteer=False, redirectTo='/settings')
    except:
      return

    neighborhood = Neighborhood.get_by_id(int(neighborhood_id))
    
    candidates_living = list(neighborhood.volunteers_living_here())
    candidates_working = list(neighborhood.volunteers_working_here())
    
    past_events = list(neighborhood.events_past()) 
    upcoming_events = list(neighborhood.events_future())    
    
    template_values = {
        'volunteer': volunteer,
        'neighborhood': neighborhood,
        'volunteers_living_here': random.sample(candidates_living, min(len(candidates_living),LIMIT)), 
        'volunteers_working_here': random.sample(candidates_working, min(len(candidates_working),LIMIT)), 
        'past_events': random.sample(past_events, min(len(past_events),LIMIT)),
        'upcoming_events':random.sample(upcoming_events, min(len(upcoming_events),LIMIT)),
      }

    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhood.html')
    self.response.out.write(template.render(path, template_values))
    return
