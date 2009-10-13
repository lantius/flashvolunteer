from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os, random

from controllers._auth import Authorize
from controllers._params import Parameters
from models.neighborhood import Neighborhood
from models.eventvolunteer import EventVolunteer
from controllers._utils import get_application

from controllers.abstract_handler import AbstractHandler

################################################################################
# Neighborhoods page
################################################################################
class NeighborhoodsPage(AbstractHandler):
  def get(self, url_data):    
    try:
      volunteer = Authorize.login(self, requireVolunteer=False, redirectTo='/settings')
    except:
      return
    
    params = Parameters.parameterize(self.request)
    
    application = get_application()
    
    neighborhoods = application.neighborhoods.order('name').fetch(limit=500)
    cnt = len(neighborhoods)
    ev = EventVolunteer.all().fetch(limit=500)               
    d = []
    LIMIT = 10
    for n in neighborhoods:                                                     
        candidates = len(list(n.volunteers_living_here())) + len(list(n.volunteers_working_here()))                   
        past_events = len(list(n.events_past()))                       
        upcoming_events = len(list(n.events_future()))                    
        d.append([str(n.key().id()), str(n.name), candidates, past_events, upcoming_events])             
        vhours = 0 
        for e in ev:
            if  e.event.neighborhood.name == n.name:                    
                if e.hours:                                           
                    vhours += e.hours
        if sum([candidates, past_events, upcoming_events]):    
            d[-1].append(vhours)
                                    
    e = [m for m in d if sum(m[2:6])]              
    for l in e: l.append(sum(l[2:6]))                                                                     
    e.sort(key=lambda x: x[6],reverse=True)                            
    for m in e:  
        y = tuple(m[2:6]) 
        m.append(y)        
    f = []
    for m in e:
        del m[2:7]               
        m = tuple(m)
        f.append(m)        
    g = tuple(f)                                       
    col1 = neighborhoods[:cnt/3]
    col2 = neighborhoods[cnt/3:2*cnt/3]
    col3 = neighborhoods[2*cnt/3:]
         
    template_values = {                              
        'neighborhoods1': col1,
        'neighborhoods2': col2,
        'neighborhoods3': col3,
        'neighborhoods': neighborhoods,                                
        'most_active_neighborhoods': g[:LIMIT],
        'LIMIT': LIMIT,                                                                       
      }
    self._add_base_template_values(vals = template_values)
    
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
    
class NeighborhoodDetailPage(AbstractHandler):
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
    
    template_values = {
        'volunteer': volunteer,
        'neighborhood': neighborhood,
        'volunteers_living_here': random.sample(candidates_living, min(len(candidates_living),LIMIT)), 
        'volunteers_working_here': random.sample(candidates_working, min(len(candidates_working),LIMIT)), 
        'past_events': past_events[-LIMIT:],
        'upcoming_events':upcoming_events[:LIMIT],
      }
    self._add_base_template_values(vals = template_values)
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhood.html')
    self.response.out.write(template.render(path, template_values))
