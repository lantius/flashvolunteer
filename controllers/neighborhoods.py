from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os, random

from controllers._auth import Authorize
from controllers._params import Parameters
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
    
    params = Parameters.parameterize(self.request)
    
    neighborhoods = Neighborhood.all().order('name').fetch(limit=500)
    cnt = len(neighborhoods)
    col1 = neighborhoods[:cnt/3]
    col2 = neighborhoods[cnt/3:2*cnt/3]
    col3 = neighborhoods[2*cnt/3:]
    
    template_values = {
        'volunteer': volunteer,
        'neighborhoods': neighborhoods, 
        'neighborhoods1': col1,
        'neighborhoods2': col2,
        'neighborhoods3': col3 
    }
    is_json = self.is_json(params)
    if is_json:
      path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhoods.json')
      render_out = template.render(path, template_values)
      if (('jsoncallback' in params)):
        render_out = params['jsoncallback'] + '(' + render_out + ');'
    else:
      path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhoods.html')
      render_out = template.render(path, template_values)
      
    self.response.out.write(render_out)
    return

  def is_json(self, params):
    if ((self.request.headers["Accept"] == "application/json") or 
         ('format' in params and params['format'] == 'json')):
       return True
    else:
       return False
    
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
    if not neighborhood:
      self.error(404)
      return

    candidates_living = list(neighborhood.volunteers_living_here())
    candidates_working = list(neighborhood.volunteers_working_here())
    
    past_events = list(neighborhood.events_past()) 
    upcoming_events = list(neighborhood.events_future())    

    session_id = ''
    if volunteer:
      session_id = volunteer.session_id
    
    template_values = {
        'volunteer': volunteer,
        'session_id' : session_id,
        'neighborhood': neighborhood,
        'volunteers_living_here': random.sample(candidates_living, min(len(candidates_living),LIMIT)), 
        'volunteers_working_here': random.sample(candidates_working, min(len(candidates_working),LIMIT)), 
        'past_events': past_events[-LIMIT:],
        'upcoming_events':upcoming_events[:LIMIT],
      }

    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhood.html')
    self.response.out.write(template.render(path, template_values))
    return
